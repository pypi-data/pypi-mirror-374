#!/usr/bin/env python3
"""
AI设计工具 - 实现 SSE 流式响应处理
RAG增强检索召回设计文档模版，结合Agent自定义「设计」智能体可实现沉浸式设计，多次交互完毕后自动化输出Joyspace设计文档。（自定义本次设计需要的Joyspace模版、需要自动生成的空间路径）

【智能体指令搭配】：
你是一名资深系统架构师，负责将业务需求任务转化为技术设计文档，生成流程图一定要用markdown格式的或者slate json来画图，千万不要用mermaid格式。
1、首先要通过design mcp传入“【设计文档模版】”，获取研发设计文档模版作为你设计内容的参照，读取本地代码库源码分析设计方案。
2、你的设计方案过程中需要与我交流沟通，有任何疑问和思考需要让我决策。
3、最终方案完备后让我选择输入“设计完毕”指令，（仅此一次）使用design mcp工具传入最终设计文档内容，提示词是：标题：你输出的设计文档标题，内容：你输出的设计文档内容 。
输入：接收需求描述和故事点（如PRD文档、用户故事、原型图）。
输出：生成符合JoySpace标准的Markdown格式设计文档。
风格：语言简洁、逻辑严谨，兼顾技术深度与可读性，避免冗余。

"""

import asyncio
import json
import os
import sys
import time
import uuid
import re
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# 导入 create_joyspace 模块
from create_joyspace import create_document_alert

# 强制刷新输出缓冲
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 设置环境变量强制输出
os.environ['PYTHONUNBUFFERED'] = '1'


def flush_print(*args, **kwargs):
    """带强制刷新的打印函数"""
    print(*args, **kwargs)
    sys.stdout.flush()


# Initialize FastMCP server
mcp = FastMCP("design")

# Autobots API 配置
AUTOBOTS_API_URL = "http://autobots-bk.jd.local/autobots/api/v1/searchAiSse"
DEFAULT_AGENT_ID = "26748"
DEFAULT_TOKEN = "97fbf17086584918ab25385acf74474b"
DEFAULT_ERP = "zhouyiru"

# 请求超时配置（300秒）
REQUEST_TIMEOUT = 300.0


def _validate_required_params(**params) -> Optional[str]:
    """
    验证必需参数的有效性
    
    Args:
        **params: 参数字典，键为参数名，值为参数值
    
    Returns:
        如果验证失败返回错误信息，否则返回 None
    """
    for param_name, param_value in params.items():
        if not param_value or not str(param_value).strip():
            return f"错误：{param_name}不能为空"
    return None


def _parse_keyword_for_document_creation(keyword: str, erp: str) -> tuple[str, str] | None:
    """
    解析 keyword 参数，提取标题和内容
    
    Args:
        keyword: 包含标题和内容的关键词字符串
        
    Returns:
        (title, content) 元组，解析失败时返回 None
        
    示例：
        输入：标题：PC端出库管理-排产管理-集合单创建-预设条件组功能增强设计文档，内容：# PC端出库管理-排产管理-集合单创建-预设条件组功能增强设计文档
        输出：("PC端出库管理-排产管理-集合单创建-预设条件组功能增强设计文档", "# PC端出库管理-排产管理-集合单创建-预设条件组功能增强设计文档")
    """
    try:
        # 使用正则表达式匹配标题和内容
        pattern = r'标题：(.+?)，内容：(.+)'
        match = re.search(pattern, keyword, re.DOTALL)
        
        if match:
            title = match.group(1).strip()
            content = match.group(2).strip()
            
            # 在内容的第一个\n\n后面添加作者信息
            # 使用传入的erp参数作为作者信息
            author = erp
            
            # 查找第一个\n\n的位置
            first_double_newline = content.find('\n\n')
            if first_double_newline != -1:
                # 在第一个\n\n后面插入作者信息
                before_part = content[:first_double_newline + 2]  # 包含\n\n
                after_part = content[first_double_newline + 2:]   # \n\n之后的内容
                content_with_author = f'{before_part}*<u>设计文档作者✍️{author}</u>*\n\n{after_part}'
            else:
                # 如果没有找到\n\n，则在内容前面添加作者信息
                content_with_author = f'*<u>设计文档作者✍️{author}</u>*\n\n{content}'
            
            return title, content_with_author
        else:
            flush_print(f"❌ 无法解析关键词格式，期望格式：标题：xxx，内容：xxx")
            return None
            
    except Exception as e:
        flush_print(f"❌ 解析关键词时发生错误：{str(e)}")
        return None


def _get_env_param(env_key: str, param_name: str) -> Optional[str]:
    """
    从环境变量获取参数值
    
    Args:
        env_key: 环境变量键名
        param_name: 参数名称（用于日志显示）
    
    Returns:
        环境变量值或 None
    """
    value = os.environ.get(env_key)
    flush_print(f"🔧 从环境变量{env_key}获取{param_name}: {value}")
    return value


async def call_autobots_sse_api(
    keyword: str,
    agent_id: str = DEFAULT_AGENT_ID,
    token: str = DEFAULT_TOKEN,
    erp: str = None,
    space_id: str = None,
    folder_id: str = None
) -> str:
    """
    AI设计工具
    
    Args:
        keyword: 查询关键词
        agent_id: Autobots 代理ID
        token: Autobots 访问令牌
        erp: 用户ERP（如果为None，将从环境变量erp获取）
        space_id: JoySpace 空间ID（如果为None，将从环境变量joySpaceId获取）
        folder_id: JoySpace 文件夹ID（如果为None，将从环境变量joyFolderId获取）
    
    Returns:
        完整的响应内容字符串
    """
    # 从环境变量获取参数（如果未提供）
    if erp is None:
        erp = _get_env_param('erp', 'erp')
    
    if space_id is None:
        space_id = _get_env_param('joySpaceId', 'space_id')
    
    if folder_id is None:
        folder_id = _get_env_param('joyFolderId', 'folder_id')
    
    # 验证必需参数
    validation_params = {
        '查询关键词': keyword,
        '代理ID': agent_id,
        '访问令牌': token,
        'erp': erp,
        'space_id': space_id,
        'folder_id': folder_id
    }
    
    error_msg = _validate_required_params(**validation_params)
    if error_msg:
        flush_print(f"❌ {error_msg}")
        return error_msg
    
    # 构建完整的查询关键词
    full_keyword = _build_full_keyword(keyword, space_id, folder_id)
    if full_keyword.startswith("❌"):
        return full_keyword
    
    # 生成请求ID和跟踪ID
    trace_id = str(uuid.uuid4())
    req_id = str(int(time.time() * 1000))
    
    # 构建HTTP请求头和请求体
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "autobots-agent-id": agent_id.strip(),
        "autobots-token": token.strip()
    }
    
    payload = {
        "traceId": trace_id,
        "reqId": req_id,
        "erp": erp.strip(),
        "keyword": full_keyword
    }
    
    # 打印请求信息
    _log_request_info(keyword, full_keyword, payload, headers)
    
    # 发送HTTP POST请求并处理SSE流式响应
    return await _process_sse_response(headers, payload)


def _compress_and_escape_string(text: str) -> str:
    """
    字符串压缩和清理工具函数
    
    功能：
    - 去除多余的换行符和空白字符
    - 压缩连续的空格为单个空格
    - 移除双引号字符
    - 返回适合JSON序列化的清理后字符串
    
    Args:
        text: 需要压缩清理的原始字符串
    
    Returns:
        压缩并清理后的字符串，可以直接用于JSON
    """
    if not text:
        return text
    
    import re
    
    # 1. 移除双引号和反斜杠
    cleaned = text.replace('"', '').replace('\\', '')
    
    # 2. 将换行符、回车符、制表符替换为空格
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # 3. 压缩多个连续空格为单个空格
    compressed = re.sub(r'\s+', ' ', cleaned)
    
    # 4. 去除首尾空白字符
    compressed = compressed.strip()
    
    return compressed


def _build_full_keyword(keyword: str, space_id: str, folder_id: str) -> str:
    """
    构建完整的查询关键词
    
    Args:
        keyword: 原始关键词
        space_id: 空间ID
        folder_id: 文件夹ID
    
    Returns:
        完整的查询关键词或错误信息
    """
    keyword_prefix = f"帮我在空间（{space_id}）的文件夹（{folder_id}）里面创建文档，标题和内容是：{keyword}"
    
    # 检测是否包含设计文档模版关键词
    if "【设计文档模版】" in keyword:
        template_name = os.environ.get('templateName')
        if template_name and template_name.strip():
            full_keyword = f"获取{template_name}的文档模版"
            flush_print(f"🔧 检测到设计文档模版请求，templateName: {template_name}")
            flush_print(f"🔧 full_keyword已替换为: {full_keyword}")
            return full_keyword
        else:
            error_msg = "❌ 错误：检测到【设计文档模版】关键词，但环境变量templateName未设置或为空"
            flush_print(error_msg)
            return error_msg
    
    # 构建完整关键词并应用压缩转义
    full_result = keyword_prefix + "\n" + keyword.strip()
    return _compress_and_escape_string(full_result)


def _log_request_info(keyword: str, full_keyword: str, payload: dict, headers: dict):
    """记录详细的请求信息（增强版调试）"""
    flush_print("=" * 60)
    flush_print("🤖 正在调用 Autobots API - 详细调试信息")
    flush_print("=" * 60)
    
    # 基本信息
    flush_print(f"🌐 接口地址：{AUTOBOTS_API_URL}")
    flush_print(f"⏱️ 请求时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    flush_print(f"⏱️ 超时设置：{REQUEST_TIMEOUT}秒")
    
    # 关键词信息
    flush_print(f"\n🔍 关键词信息：")
    flush_print(f"   原始关键词：{keyword}")
    flush_print(f"   原始关键词长度：{len(keyword)}字符")
    flush_print(f"   完整查询关键词：{full_keyword}")
    flush_print(f"   完整关键词长度：{len(full_keyword)}字符")
    
    # 请求参数详情
    flush_print(f"\n📋 请求参数详情：")
    for key, value in payload.items():
        if key == 'keyword':
            flush_print(f"   {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
            flush_print(f"   {key}_length: {len(str(value))}字符")
        else:
            flush_print(f"   {key}: {value}")
    
    flush_print(f"\n📋 完整请求参数JSON：")
    flush_print(json.dumps(payload, ensure_ascii=False, indent=2))
    
    # 请求头详情
    flush_print(f"\n📋 请求头信息：")
    for key, value in headers.items():
        if 'token' in key.lower():
            # 隐藏敏感token信息
            masked_value = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else '*' * len(value)
            flush_print(f"   {key}: {masked_value}")
        else:
            flush_print(f"   {key}: {value}")
    
    # 环境变量信息
    flush_print(f"\n🔧 相关环境变量：")
    env_vars = ['erp', 'joySpaceId', 'joyFolderId', 'templateName']
    for env_var in env_vars:
        value = os.environ.get(env_var)
        status = "✅ 已设置" if value else "❌ 未设置"
        display_value = value if value else "未设置"
        flush_print(f"   {env_var}: {display_value} {status}")
    
    flush_print("=" * 60)


async def _check_network_connectivity() -> tuple[bool, str]:
    """
    检查网络连接性
    
    Returns:
        (is_connected, message): 连接状态和消息
    """
    try:
        # 检查基本网络连接
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 尝试连接到目标API服务器
            try:
                response = await client.get(AUTOBOTS_API_URL.replace('/searchAiSse', '/health'), timeout=5.0)
                return True, f"✅ 网络连接正常，服务器可达"
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return True, f"✅ 网络连接正常，服务器可达（健康检查端点不存在，这是正常的）"
                else:
                    return False, f"❌ 服务器响应错误：HTTP {e.response.status_code}"
            except httpx.TimeoutException:
                return False, f"❌ 连接超时：无法在5秒内连接到服务器"
            except httpx.ConnectError:
                return False, f"❌ 连接失败：无法连接到服务器 {AUTOBOTS_API_URL}"
            except Exception as e:
                return False, f"❌ 网络检查失败：{str(e)}"
    except Exception as e:
        return False, f"❌ 网络检查异常：{str(e)}"


async def _process_sse_response(headers: dict, payload: dict) -> str:
    """
    处理SSE流式响应（增强版调试信息）
    
    Args:
        headers: 请求头
        payload: 请求体
    
    Returns:
        完整的响应内容字符串或错误信息
    """
    response_content = ""  # 改为字符串，只保留最后一次响应
    response_lines_count = 0
    start_time = time.time()
    
    # 先检查网络连接
    flush_print("🔍 检查网络连接...")
    is_connected, network_msg = await _check_network_connectivity()
    flush_print(network_msg)
    
    if not is_connected:
        return f"❌ 网络连接检查失败：{network_msg}"
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            flush_print(f"🚀 发起HTTP请求到：{AUTOBOTS_API_URL}")
            flush_print(f"⏱️ 请求开始时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            async with client.stream(
                "POST",
                AUTOBOTS_API_URL,
                headers=headers,
                json=payload
            ) as response:
                
                # 详细的HTTP响应信息
                flush_print(f"📊 HTTP状态码：{response.status_code}")
                flush_print(f"📋 响应头信息：{dict(response.headers)}")
                
                if response.status_code != 200:
                    error_details = {
                        "status_code": response.status_code,
                        "reason_phrase": response.reason_phrase,
                        "headers": dict(response.headers),
                        "request_url": str(response.url),
                        "request_method": response.request.method
                    }
                    
                    try:
                        error_body = await response.aread()
                        error_details["response_body"] = error_body.decode('utf-8', errors='ignore')
                    except Exception:
                        error_details["response_body"] = "无法读取响应体"
                    
                    error_msg = f"""❌ HTTP请求失败详情：
🔍 状态码：{error_details['status_code']} ({error_details['reason_phrase']})
🌐 请求URL：{error_details['request_url']}
📋 请求方法：{error_details['request_method']}
📄 响应头：{json.dumps(error_details['headers'], ensure_ascii=False, indent=2)}
📄 响应体：{error_details['response_body'][:500]}{'...' if len(error_details['response_body']) > 500 else ''}
💡 建议：请检查API配置、令牌有效性或联系管理员"""
                    
                    flush_print(error_msg)
                    return error_msg
                
                # 逐行读取SSE流式响应
                flush_print("📡 开始接收SSE流式响应...")
                flush_print("-" * 50)
                
                async for line in response.aiter_lines():
                    if line and line.strip():
                        response_lines_count += 1
                        current_time = time.time()
                        elapsed = current_time - start_time
                        
                        flush_print(f"📨 [{response_lines_count}] ({elapsed:.1f}s) 接收到数据：{line[:200]}{'...' if len(line) > 200 else ''}")
                        response_content = line  # 只保留最后一次响应，覆盖之前的内容
                
                end_time = time.time()
                total_elapsed = end_time - start_time
                
                flush_print("-" * 50)
                flush_print(f"✅ SSE流式响应接收完成")
                flush_print(f"📊 总共接收 {response_lines_count} 行数据，耗时 {total_elapsed:.2f} 秒")
                
        except httpx.TimeoutException as e:
            elapsed = time.time() - start_time
            error_msg = f"""❌ 请求超时详情：
⏱️ 超时时间：{REQUEST_TIMEOUT}秒
⏱️ 实际耗时：{elapsed:.2f}秒
🔍 超时类型：{type(e).__name__}
🌐 目标URL：{AUTOBOTS_API_URL}
💡 建议：检查网络连接或增加超时时间"""
            flush_print(error_msg)
            return error_msg
            
        except httpx.HTTPStatusError as e:
            error_msg = f"""❌ HTTP状态错误详情：
📊 状态码：{e.response.status_code}
🔍 错误原因：{e.response.reason_phrase}
🌐 请求URL：{e.request.url}
📋 请求方法：{e.request.method}
📄 错误响应体：{e.response.text[:500]}{'...' if len(e.response.text) > 500 else ''}
💡 建议：检查API端点和参数配置"""
            flush_print(error_msg)
            return error_msg
            
        except httpx.RequestError as e:
            error_msg = f"""❌ 请求错误详情：
🔍 错误类型：{type(e).__name__}
📄 错误信息：{str(e)}
🌐 目标URL：{AUTOBOTS_API_URL}
💡 建议：检查网络连接、DNS解析或防火墙设置"""
            flush_print(error_msg)
            return error_msg
            
        except Exception as e:
            import traceback
            error_msg = f"""❌ 未知错误详情：
🔍 错误类型：{type(e).__name__}
📄 错误信息：{str(e)}
🔍 错误堆栈：
{traceback.format_exc()}
💡 建议：这可能是代码bug，请联系开发者"""
            flush_print(error_msg)
            return error_msg
    
    # 处理并返回最后一次响应内容
    if response_content:
        flush_print(f"📄 最终响应内容（长度：{len(response_content)}字符）：")
        flush_print(f"📄 响应内容预览：{response_content[:300]}{'...' if len(response_content) > 300 else ''}")
        flush_print(f"📄 完整响应内容：")
        flush_print(response_content)
        return response_content
    else:
        error_msg = f"""❌ 未接收到任何响应数据：
📊 接收行数：{response_lines_count}
⏱️ 总耗时：{time.time() - start_time:.2f}秒
💡 建议：检查API是否正常工作或联系管理员"""
        flush_print(error_msg)
        return error_msg


@mcp.tool()
async def ai_design(
    keyword: str
) -> str:
    """
    AI设计工具（SSE 流式响应）- 增强版调试
    
    Args:
        keyword: 查询关键词或文档创建指令
        
    注意：
        - agent_id 和 token 使用系统默认常量
        - erp、space_id、folder_id 从环境变量读取
        - templateName: 设计文档模版名称（可选，需要联系zhouyiru知识库投喂）
    """
    
    # 记录函数调用开始
    start_time = time.time()
    flush_print("🚀 ai_design 函数调用开始")
    flush_print("=" * 60)
    
    # 从环境变量读取参数
    agent_id = DEFAULT_AGENT_ID
    token = DEFAULT_TOKEN
    erp = os.getenv('erp', DEFAULT_ERP)
    space_id = os.getenv('joySpaceId')
    folder_id = os.getenv('joyFolderId')
    
    # 记录输入参数
    flush_print("📋 输入参数详情：")
    flush_print(f"   keyword: {keyword}")
    flush_print(f"   keyword_length: {len(keyword) if keyword else 0}字符")
    flush_print(f"   agent_id: {agent_id} (常量)")
    flush_print(f"   token: {token[:8]}***{token[-4:] if len(token) > 12 else '***'} (常量)")
    flush_print(f"   erp: {erp} (环境变量)")
    flush_print(f"   space_id: {space_id} (环境变量)")
    flush_print(f"   folder_id: {folder_id} (环境变量)")
    
    # 验证输入参数
    if not keyword or not keyword.strip():
        error_msg = f"""❌ 参数验证失败：
🔍 错误原因：查询关键词不能为空
📋 输入参数：keyword = '{keyword}'
💡 建议：请提供有效的查询关键词"""
        flush_print(error_msg)
        return error_msg
    
    # 检测是否包含设计文档模版关键词 - 保留原有逻辑
    if "【设计文档模版】" in keyword:
        flush_print("🔧 检测到设计文档模版请求，使用原有接口")
        # 调用原有的 API
        result = await call_autobots_sse_api(
            keyword=keyword.strip(),
            agent_id=agent_id,
            token=token,
            erp=erp,
            space_id=space_id,
            folder_id=folder_id
        )
        
        # 格式化返回结果（增强版调试信息）
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if result.startswith("错误：") or result.startswith("❌"):
            error_result = f"""❌ AI设计失败！（设计文档模版请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
� 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ 执行耗时: {elapsed_time:.2f}秒
❌ 详细错误信息:
{result}
💡 建议: 请检查网络连接、API配置、环境变量设置或联系管理员"""
            flush_print(f"❌ 设计文档模版请求失败，耗时 {elapsed_time:.2f}秒")
            return error_result
        else:
            success_result = f"""✅ AI设计成功！（设计文档模版请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
👤 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ 执行耗时: {elapsed_time:.2f}秒
📄 搜索结果:
{result}"""
            flush_print(f"✅ 设计文档模版请求成功，耗时 {elapsed_time:.2f}秒")
            return success_result
    
    # 检测是否为文档创建请求（包含"标题："和"内容："）
    elif "标题：" in keyword and "内容：" in keyword:
        flush_print("🔧 检测到文档创建请求，使用新接口 create_document_alert")
        
        # 参数已在函数开始处从环境变量读取，无需重复获取
        
        # 验证必需参数
        validation_params = {
            '查询关键词': keyword,
            'erp': erp,
            'space_id': space_id,
            'folder_id': folder_id
        }
        
        error_msg = _validate_required_params(**validation_params)
        if error_msg:
            flush_print(f"❌ {error_msg}")
            return error_msg
        
        # 解析标题和内容
        parsed_result = _parse_keyword_for_document_creation(keyword, erp)
        if not parsed_result:
            return "❌ 错误：无法解析文档标题和内容，请检查格式是否正确（期望格式：标题：xxx，内容：xxx）"
        
        title, content = parsed_result
        
        try:
            # 记录文档创建开始时间
            doc_start_time = time.time()
            flush_print(f"📄 开始创建文档：{title}")
            flush_print(f"📄 文档内容长度：{len(content)}字符")
            
            # 调用新的文档创建接口
            result = await create_document_alert(
                title=title,
                content=content,
                folder_id=folder_id,
                team_id=space_id  # space_id 也对应 team_id
            )
            
            # 计算文档创建耗时
            doc_end_time = time.time()
            doc_elapsed = doc_end_time - doc_start_time
            total_elapsed = doc_end_time - start_time
            
            success_result = f"""✅ 文档创建请求已处理！（文档创建请求）
🔍 原始关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
📄 解析标题: {title}
📄 标题长度: {len(title)}字符
📄 文档内容长度: {len(content)}字符
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ 文档创建耗时: {doc_elapsed:.2f}秒
⏱️ 总执行耗时: {total_elapsed:.2f}秒
📄 创建结果:
{result}"""
            
            flush_print(f"✅ 文档创建成功，创建耗时 {doc_elapsed:.2f}秒，总耗时 {total_elapsed:.2f}秒")
            return success_result
            
        except Exception as e:
            import traceback
            doc_end_time = time.time()
            doc_elapsed = doc_end_time - start_time
            
            error_msg = f"""❌ 文档创建接口调用失败！（文档创建请求）
🔍 原始关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
📄 解析标题: {title}
📄 标题长度: {len(title)}字符
📄 文档内容长度: {len(content)}字符
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ 失败前耗时: {doc_elapsed:.2f}秒
❌ 详细错误信息:
🔍 错误类型: {type(e).__name__}
📄 错误消息: {str(e)}
🔍 错误堆栈:
{traceback.format_exc()}
💡 建议: 请检查JoySpace API配置、网络连接或联系管理员"""
            
            flush_print(error_msg)
            return error_msg
    
    else:
        # 其他情况使用原有的 API 逻辑
        flush_print("🔧 使用原有 Autobots API 接口")
        
        # 参数已在函数开始处从环境变量读取，无需重复获取
        
        # 验证必需参数
        validation_params = {
            '查询关键词': keyword,
            'erp': erp,
            'space_id': space_id,
            'folder_id': folder_id
        }
        
        error_msg = _validate_required_params(**validation_params)
        if error_msg:
            flush_print(f"❌ {error_msg}")
            return f"""❌ 参数验证失败！（普通API请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
❌ 验证错误: {error_msg}
💡 建议: 请检查环境变量设置或提供完整的参数"""
        
        try:
            # 记录API调用开始时间
            api_start_time = time.time()
            
            result = await call_autobots_sse_api(
                keyword=keyword.strip(),
                agent_id=agent_id,
                token=token,
                erp=erp,
                space_id=space_id,
                folder_id=folder_id
            )
            
            # 计算API调用耗时
            api_end_time = time.time()
            api_elapsed = api_end_time - api_start_time
            total_elapsed = api_end_time - start_time
            
            # 格式化返回结果（增强版调试信息）
            if result.startswith("错误：") or result.startswith("❌"):
                error_result = f"""❌ AI设计失败！（普通API请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ API调用耗时: {api_elapsed:.2f}秒
⏱️ 总执行耗时: {total_elapsed:.2f}秒
❌ 详细错误信息:
{result}
💡 建议: 请检查网络连接、API配置、环境变量设置或联系管理员"""
                flush_print(f"❌ 普通API请求失败，API耗时 {api_elapsed:.2f}秒，总耗时 {total_elapsed:.2f}秒")
                return error_result
            else:
                success_result = f"""✅ AI设计成功！（普通API请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ API调用耗时: {api_elapsed:.2f}秒
⏱️ 总执行耗时: {total_elapsed:.2f}秒
📄 响应结果长度: {len(result)}字符
📄 搜索结果:
{result}"""
                flush_print(f"✅ 普通API请求成功，API耗时 {api_elapsed:.2f}秒，总耗时 {total_elapsed:.2f}秒")
                return success_result
                
        except Exception as e:
            import traceback
            api_end_time = time.time()
            api_elapsed = api_end_time - start_time
            
            error_msg = f"""❌ 普通API调用异常！（普通API请求）
🔍 查询关键词: {keyword}
🔍 关键词长度: {len(keyword)}字符
🤖 代理ID: {agent_id}
🔑 令牌: {token[:8]}***{token[-4:]}
? 用户ERP: {erp}
🏢 空间ID: {space_id}
📁 文件夹ID: {folder_id}
⏱️ 异常前耗时: {api_elapsed:.2f}秒
❌ 详细异常信息:
🔍 异常类型: {type(e).__name__}
📄 异常消息: {str(e)}
🔍 异常堆栈:
{traceback.format_exc()}
💡 建议: 请检查网络连接、API配置或联系管理员"""
            
            flush_print(error_msg)
            return error_msg


@mcp.prompt()
async def sse_response_filter() -> str:
    """
    SSE流式响应过滤提示词
    
    用于指导在调用call_autobots_sse_api创建设计文档时，
    SSE模式中间过程的响应不用返回用户，判断到最后完成了返回最后一次结果即可。
    """
    return """在处理call_autobots_sse_api接口SSE流式响应时，请遵循以下规则：

1. **中间过程响应处理**：
   - SSE流式响应的中间过程数据不需要返回给用户
   - 只有当检测到响应完成时，才返回最终结果
   - 避免向用户展示过多的中间状态信息

2. **完成状态判断**：
   - 监听SSE流的结束信号
   - 当接收到完整的响应数据后，进行最终处理
   - 确保返回的是完整、有意义的最终结果

3. **用户体验优化**：
   - 减少不必要的中间信息输出
   - 提供清晰、简洁的最终结果
   - 保持响应的专业性和可读性

4. **错误处理**：
   - 如果在SSE过程中发生错误，及时返回错误信息
   - 确保用户能够了解操作的最终状态
   - 提供有用的错误诊断信息

请在调用call_autobots_sse_api时应用这些原则，确保用户获得最佳的交互体验。"""


async def interactive_mode():
    """交互式模式 - 允许用户直接操作 Autobots API"""
    flush_print("🤖 欢迎使用 AI设计工具！")
    flush_print("=" * 50)
    
    while True:
        flush_print("\n📋 请选择操作：")
        flush_print("1. AI 搜索查询")
        flush_print("2. 启动 MCP 服务器模式")
        flush_print("3. 退出程序")
        
        try:
            choice = input("\n请输入选项 (1-3): ").strip()
            
            if choice == "1":
                await search_interactive()
            elif choice == "2":
                flush_print("🚀 启动 MCP 服务器模式...")
                flush_print("💡 提示：需要退出交互式模式来启动 MCP 服务器")
                flush_print("🔄 请使用 'uv run design.py --mcp' 命令直接启动 MCP 服务器")
                flush_print("⚠️ 或者选择退出程序，然后重新运行")
                break
            elif choice == "3":
                flush_print("👋 再见！")
                break
            else:
                flush_print("❌ 无效选项，请输入 1-3")
                
        except KeyboardInterrupt:
            flush_print("\n👋 程序已退出")
            break
        except Exception as e:
            flush_print(f"❌ 发生错误：{str(e)}")


async def search_interactive():
    """交互式AI搜索"""
    flush_print("\n🔍 AI 搜索查询")
    flush_print("-" * 30)
    
    try:
        keyword = input("请输入查询关键词: ").strip()
        if not keyword:
            flush_print("❌ 查询关键词不能为空")
            return
            
        agent_id = input(f"请输入代理ID (默认: {DEFAULT_AGENT_ID}): ").strip()
        if not agent_id:
            agent_id = DEFAULT_AGENT_ID
            
        token = input(f"请输入访问令牌 (默认: {DEFAULT_TOKEN}): ").strip()
        if not token:
            token = DEFAULT_TOKEN
            
        erp = input(f"请输入用户ERP (默认: {DEFAULT_ERP}): ").strip()
        if not erp:
            erp = DEFAULT_ERP
            
        space_id = input("请输入空间ID (可选，直接回车跳过): ").strip() or None
        folder_id = input("请输入文件夹ID (可选，直接回车跳过): ").strip() or None
        
        flush_print("\n🚀 开始AI搜索...")
        result = await call_autobots_sse_api(
            keyword=keyword,
            agent_id=agent_id,
            token=token,
            erp=erp,
            space_id=space_id,
            folder_id=folder_id
        )
        
        if not result.startswith("错误：") and not result.startswith("❌"):
            flush_print("\n🎉 AI搜索完成！")
        else:
            flush_print("\n❌ AI搜索失败")
            
    except KeyboardInterrupt:
        flush_print("\n⏹️ 操作已取消")
    except Exception as e:
        flush_print(f"\n❌ 发生错误：{str(e)}")


async def run_ai_design_test(scenario):
    """运行 ai_design 函数测试"""
    flush_print(f"\n🚀 开始测试：{scenario['name']}")
    flush_print("-" * 50)
    
    try:
        # 获取测试参数
        if scenario['keyword']:
            keyword = scenario['keyword']
            flush_print(f"📝 使用预设关键词：{keyword}")
        else:
            keyword = input("请输入查询关键词: ").strip()
            if not keyword:
                flush_print("❌ 查询关键词不能为空")
                return
        
        # 获取可选参数
        flush_print("\n🔧 配置测试参数（直接回车使用默认值或环境变量）：")
        
        agent_id = input(f"代理ID (默认: {DEFAULT_AGENT_ID}): ").strip()
        if not agent_id:
            agent_id = DEFAULT_AGENT_ID
            
        token = input(f"访问令牌 (默认: {DEFAULT_TOKEN}): ").strip()
        if not token:
            token = DEFAULT_TOKEN
            
        erp = input(f"用户ERP (默认从环境变量获取): ").strip() or None
        space_id = input(f"空间ID (默认从环境变量获取): ").strip() or None
        folder_id = input(f"文件夹ID (默认从环境变量获取): ").strip() or None
        
        # 显示测试参数
        flush_print("\n📋 测试参数总览：")
        flush_print(f"🔍 关键词: {keyword}")
        flush_print(f"🤖 代理ID: {agent_id}")
        flush_print(f"🔑 令牌: {token[:10]}..." if len(token) > 10 else f"🔑 令牌: {token}")
        flush_print(f"👤 ERP: {erp or '从环境变量获取'}")
        flush_print(f"🏢 空间ID: {space_id or '从环境变量获取'}")
        flush_print(f"📁 文件夹ID: {folder_id or '从环境变量获取'}")
        
        # 确认执行
        confirm = input("\n是否执行测试？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            flush_print("⏹️ 测试已取消")
            return
        
        # 执行 ai_design 函数
        flush_print("\n🚀 正在执行 ai_design 函数...")
        flush_print("=" * 50)
        
        result = await ai_design(
            keyword=keyword,
            agent_id=agent_id,
            token=token,
            erp=erp,
            space_id=space_id,
            folder_id=folder_id
        )
        
        flush_print("=" * 50)
        flush_print("✅ 测试执行完成！")
        flush_print(f"\n📄 执行结果：\n{result}")
        
        # 询问是否保存结果
        save_result = input("\n是否保存测试结果到文件？(y/N): ").strip().lower()
        if save_result in ['y', 'yes']:
            await save_test_result(scenario['name'], keyword, result)
            
    except KeyboardInterrupt:
        flush_print("\n⏹️ 测试已取消")
    except Exception as e:
        flush_print(f"\n❌ 测试执行错误：{str(e)}")
        import traceback
        flush_print(f"🔍 详细错误信息：\n{traceback.format_exc()}")


def show_environment_config():
    """显示当前环境变量配置"""
    flush_print("\n🔧 当前环境变量配置：")
    flush_print("-" * 30)
    
    env_vars = {
        'erp': '用户ERP',
        'joySpaceId': '空间ID',
        'joyFolderId': '文件夹ID',
        'templateName': '模版名称'
    }
    
    for env_key, description in env_vars.items():
        value = os.environ.get(env_key)
        status = "✅ 已设置" if value else "❌ 未设置"
        display_value = value if value else "未设置"
        flush_print(f"{description} ({env_key}): {display_value} {status}")
    
    flush_print(f"\n🌐 API配置：")
    flush_print(f"接口地址: {AUTOBOTS_API_URL}")
    flush_print(f"默认代理ID: {DEFAULT_AGENT_ID}")
    flush_print(f"默认令牌: {DEFAULT_TOKEN[:10]}..." if len(DEFAULT_TOKEN) > 10 else f"默认令牌: {DEFAULT_TOKEN}")
    flush_print(f"默认ERP: {DEFAULT_ERP}")


def set_environment_variables():
    """设置环境变量"""
    flush_print("\n🔧 设置环境变量")
    flush_print("-" * 20)
    flush_print("💡 提示：直接回车跳过该项设置")
    
    env_vars = {
        'erp': '用户ERP',
        'joySpaceId': '空间ID',
        'joyFolderId': '文件夹ID',
        'templateName': '模版名称'
    }
    
    for env_key, description in env_vars.items():
        current_value = os.environ.get(env_key, "未设置")
        new_value = input(f"{description} (当前: {current_value}): ").strip()
        
        if new_value:
            os.environ[env_key] = new_value
            flush_print(f"✅ {description} 已设置为: {new_value}")
        else:
            flush_print(f"⏭️ 跳过 {description} 设置")
    
    flush_print("\n✅ 环境变量设置完成！")


def show_help():
    """显示帮助信息"""
    flush_print(f"""🎯 AI设计工具使用说明

运行模式：
  uv run design.py                    # 交互式模式
  uv run design.py --mcp             # 直接启动 MCP 服务器
  uv run design.py --help            # 显示帮助信息

交互式模式功能：
  1. AI 搜索查询 - 通过交互式界面进行AI搜索
  2. 启动 MCP 服务器 - 切换到 MCP 服务器模式
  3. 退出程序

MCP 服务器模式：
  - 通过 stdio 传输运行
  - 等待 MCP 客户端连接
  - 提供 ai_design 工具

API 配置：
  - 接口地址: {AUTOBOTS_API_URL}
  - 默认代理ID: {DEFAULT_AGENT_ID}
  - 默认令牌: {DEFAULT_TOKEN}
  - 默认ERP: {DEFAULT_ERP}
  - 请求超时: {REQUEST_TIMEOUT}秒

环境变量配置：
  - erp: 用户ERP标识
  - joySpaceId: JoySpace空间ID
  - joyFolderId: JoySpace文件夹ID
  - templateName: 设计文档模版名称""")


def main_sync():
    """同步主函数，处理 MCP 服务器启动"""
    flush_print("🔧 AI设计工具启动中...")
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            show_help()
        elif arg == '--mcp':
            flush_print("🚀 启动 MCP 服务器模式...")
            # 直接使用正确的 FastMCP 启动方式，避免事件循环冲突
            mcp.run(transport='stdio')
        else:
            flush_print(f"❌ 未知参数: {arg}")
            show_help()
    else:
        # 默认交互式模式需要异步运行
        try:
            asyncio.run(interactive_mode())
        except KeyboardInterrupt:
            flush_print("\n👋 程序已退出")
        except Exception as e:
            flush_print(f"❌ 交互式模式运行错误：{str(e)}")


if __name__ == "__main__":
    try:
        main_sync()
    except KeyboardInterrupt:
        flush_print("\n👋 程序已退出")
    except Exception as e:
        flush_print(f"❌ 程序运行错误：{str(e)}")