#!/usr/bin/env python3
"""
JoySpace 文档创建工具 - 修复输出显示问题的版本
"""

import asyncio
import sys
import os
from typing import Any, Optional
import httpx
import json
from mcp.server.fastmcp import FastMCP

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

# Joyspace API 配置 - 接口地址常量化
JS_API_BASE = "http://openme.jd.local/open-api/suite/v1/joyspace/createPage"
APP_ACCESS_TOKEN_API = "http://openme.jd.local/open-api/auth/v1/app_access_token"
TEAM_ACCESS_TOKEN_API = "http://openme.jd.local/open-api/auth/v1/team_access_token"
OPEN_USER_INFO_API = "http://openme.jd.local/open-api/custom/v1/getOpenUserInfoInner"  # 新增：开放用户信息接口常量
USER_TICKET = "e4bCtVF3Whglr2n8PZwg"

# 应用凭证配置
APP_KEY = "AZ1eE0CXULxxg7Mc1Wou"
APP_SECRET = "e4bCtVF3Whglr2n8PZwg"
Open_Team_ID = "eb7fb0f25a7c0b66e2cd96f2fcb2ac96"

# 场景参数常量
SCENE = "AiCreateForMcp"

# 缓存相关
import time
from typing import Dict, Tuple

# 全局缓存变量
_app_access_token_cache: Dict[str, Tuple[str, float]] = {}
_team_access_token_cache: Dict[str, Tuple[str, float]] = {}



async def get_app_access_token(
    app_key: str = APP_KEY,
    app_secret: str = APP_SECRET,
    force_refresh: bool = False
) -> str | None:
    """
    获取应用访问令牌 (appAccessToken)
    
    Args:
        app_key: 应用Key
        app_secret: 应用秘钥
        force_refresh: 是否强制刷新token
    
    Returns:
        应用访问令牌字符串，失败时返回 None
        
    说明：
        - appAccessToken的最大有效期是30天
        - 如果在有效期小于10分钟的情况下调用，会返回一个新的appAccessToken
        - 推荐缓存，缓存时间参考返回的expireIn字段
        - 频繁调用此接口会被限制访问
    """
    global _app_access_token_cache
    
    # 1、验证输入参数的有效性
    if not app_key or not app_key.strip():
        flush_print("❌ 错误：应用Key不能为空")
        return None
    
    if not app_secret or not app_secret.strip():
        flush_print("❌ 错误：应用秘钥不能为空")
        return None
    
    cache_key = f"{app_key}:{app_secret}"
    current_time = time.time()
    
    # 2、检查缓存中是否存在有效的令牌
    if not force_refresh and cache_key in _app_access_token_cache:
        cached_token, expire_time = _app_access_token_cache[cache_key]
        
        # 如果距离过期时间还有超过10分钟（600秒），使用缓存
        if current_time < expire_time - 600:
            flush_print(f"🔄 使用缓存的应用访问令牌（剩余有效期：{int((expire_time - current_time) / 60)}分钟）")
            return cached_token
        else:
            flush_print("⏰ 缓存的令牌即将过期（小于10分钟），正在刷新...")
    
    # 3、构建HTTP请求头和请求体
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    payload = {
        "appKey": app_key.strip(),
        "appSecret": app_secret.strip()
    }
    
    flush_print(f"🔐 正在获取应用访问令牌...")
    flush_print(f"📋 请求参数：{json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    # 4、发送HTTP POST请求到应用访问令牌接口
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                APP_ACCESS_TOKEN_API,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # 5、检查接口返回的状态码
            if result.get("code") != 0:
                flush_print(f"❌ 获取应用访问令牌失败：{result.get('msg', '未知错误')}")
                return None
            
            # 6、提取并验证返回的令牌数据
            data = result.get("data", {})
            app_access_token = data.get("appAccessToken")
            expire_in = data.get("expireIn", 0)
            
            if not app_access_token:
                flush_print("❌ 错误：接口返回的应用访问令牌为空")
                return None
            
            if expire_in <= 0:
                flush_print("❌ 错误：接口返回的有效期无效")
                return None
            
            # 7、更新缓存并返回令牌
            expire_time = current_time + expire_in
            _app_access_token_cache[cache_key] = (app_access_token, expire_time)
            
            flush_print(f"✅ 成功获取应用访问令牌")
            flush_print(f"⏰ 有效期：{expire_in}秒（约{expire_in // 86400}天）")
            flush_print(f"📅 过期时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time))}")
            
            return app_access_token
            
        except httpx.HTTPStatusError as e:
            flush_print(f"❌ 应用访问令牌接口HTTP错误：状态码 {e.response.status_code}")
            flush_print(f"📄 错误响应：{e.response.text}")
            return None
        except httpx.TimeoutException:
            flush_print("❌ 错误：应用访问令牌接口请求超时")
            return None
        except httpx.RequestError as e:
            flush_print(f"❌ 应用访问令牌接口请求错误：{str(e)}")
            return None
        except json.JSONDecodeError:
            flush_print("❌ 错误：应用访问令牌接口响应不是有效的JSON格式")
            return None
        except Exception as e:
            flush_print(f"❌ 应用访问令牌接口未知错误：{str(e)}")
            return None


async def get_team_access_token(
    app_access_token: str,
    open_team_id: str = Open_Team_ID,
    force_refresh: bool = False
) -> str | None:
    """
    获取团队访问令牌 (teamAccessToken)
    
    Args:
        app_access_token: 应用访问令牌
        open_team_id: 开放teamId
        force_refresh: 是否强制刷新token
    
    Returns:
        团队访问令牌字符串，失败时返回 None
    """
    global _team_access_token_cache
    
    # 1、验证输入参数的有效性
    if not app_access_token or not app_access_token.strip():
        flush_print("❌ 错误：应用访问令牌不能为空")
        return None
    
    if not open_team_id or not open_team_id.strip():
        flush_print("❌ 错误：开放teamId不能为空")
        return None
    
    cache_key = f"{app_access_token}:{open_team_id}"
    current_time = time.time()
    
    # 2、检查缓存中是否存在有效的团队令牌
    if not force_refresh and cache_key in _team_access_token_cache:
        cached_token, expire_time = _team_access_token_cache[cache_key]
        
        # 如果距离过期时间还有超过5分钟（300秒），使用缓存
        if current_time < expire_time - 300:
            flush_print(f"🔄 使用缓存的团队访问令牌（剩余有效期：{int((expire_time - current_time) / 60)}分钟）")
            return cached_token
        else:
            flush_print("⏰ 缓存的团队令牌即将过期（小于5分钟），正在刷新...")
    
    # 3、构建HTTP请求头和请求体
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    payload = {
        "appAccessToken": app_access_token.strip(),
        "openTeamId": open_team_id.strip()
    }
    
    flush_print(f"🔐 正在获取团队访问令牌...")
    flush_print(f"📋 请求参数：{json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    # 4、发送HTTP POST请求到团队访问令牌接口
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                TEAM_ACCESS_TOKEN_API,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # 5、检查接口返回的状态码
            if result.get("code") != 0:
                flush_print(f"❌ 获取团队访问令牌失败：{result.get('msg', '未知错误')}")
                return None
            
            # 6、提取并验证返回的令牌数据
            data = result.get("data", {})
            team_access_token = data.get("teamAccessToken")
            expire_in = data.get("expireIn", 0)
            
            if not team_access_token:
                flush_print("❌ 错误：接口返回的团队访问令牌为空")
                return None
            
            if expire_in <= 0:
                flush_print("❌ 错误：接口返回的有效期无效")
                return None
            
            # 7、更新缓存并返回令牌
            expire_time = current_time + expire_in
            _team_access_token_cache[cache_key] = (team_access_token, expire_time)
            
            flush_print(f"✅ 成功获取团队访问令牌")
            flush_print(f"⏰ 有效期：{expire_in}秒（约{expire_in // 60}分钟）")
            flush_print(f"📅 过期时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expire_time))}")
            
            return team_access_token
            
        except httpx.HTTPStatusError as e:
            flush_print(f"❌ 团队访问令牌接口HTTP错误：状态码 {e.response.status_code}")
            flush_print(f"📄 错误响应：{e.response.text}")
            return None
        except httpx.TimeoutException:
            flush_print("❌ 错误：团队访问令牌接口请求超时")
            return None
        except httpx.RequestError as e:
            flush_print(f"❌ 团队访问令牌接口请求错误：{str(e)}")
            return None
        except json.JSONDecodeError:
            flush_print("❌ 错误：团队访问令牌接口响应不是有效的JSON格式")
            return None
        except Exception as e:
            flush_print(f"❌ 团队访问令牌接口未知错误：{str(e)}")
            return None


async def get_open_user_info(
    team_access_token: str,
    user_id: str = "org.ai.code.review1",
    team_id: str = "00046419",
    app_key: str = APP_KEY
) -> str | None:
    """
    获取开放用户信息，替换原来的get_access_token函数
    
    Args:
        team_access_token: 团队访问令牌
        user_id: 用户ID，默认为org.ai.code.review1
        team_id: 团队ID，默认为Open_Team_ID
        app_key: 应用Key，默认为APP_KEY
        host: 主机地址，默认为http://openme.jd.local
    
    Returns:
        开放用户ID字符串，失败时返回 None
    """
    # 1、验证输入参数的有效性
    if not team_access_token or not team_access_token.strip():
        flush_print("❌ 错误：团队访问令牌不能为空")
        return None
    
    if not user_id or not user_id.strip():
        flush_print("❌ 错误：用户ID不能为空")
        return None
    
    if not team_id or not team_id.strip():
        flush_print("❌ 错误：团队ID不能为空")
        return None
    
    if not app_key or not app_key.strip():
        flush_print("❌ 错误：应用Key不能为空")
        return None
    
    # 2、构建接口地址（使用常量）
    api_url = f"{OPEN_USER_INFO_API}"
    
    # 3、构建HTTP请求头
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {team_access_token}"
    }
    
    # 4、构建请求体 - 修复：teamId固定使用"00046419"
    payload = {
        "getOpenUserInfo": {
            "userId": user_id.strip(),
            "teamId": "00046419",  # 修复：固定传入正确的团队ID
            "appKey": app_key.strip()
        }
    }
    
    flush_print(f"🔐 正在获取开放用户信息...")
    flush_print(f"🌐 接口地址：{api_url}")
    flush_print(f"📋 请求参数：{json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    # 5、发送HTTP POST请求到新的接口
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # 6、检查接口返回的状态码
            if result.get("code") != 0:
                flush_print(f"❌ 获取开放用户信息失败：{result.get('msg', '未知错误')}")
                return None
            
            # 7、提取并验证返回的开放用户ID
            data = result.get("data", {})
            open_user_info_resp = data.get("getOpenUserInfoRespDto", {})
            open_user_id = open_user_info_resp.get("openUserId")
            
            if not open_user_id:
                flush_print("❌ 错误：接口返回的开放用户ID为空")
                flush_print(f"📄 完整响应：{json.dumps(result, ensure_ascii=False, indent=2)}")
                return None
            
            # 8、输出成功信息
            flush_print(f"✅ 成功获取开放用户信息")
            flush_print(f"👤 开放用户ID：{open_user_id}")
            flush_print(f"👨‍💼 用户ID：{user_id}")
            flush_print(f"🏢 团队ID：{team_id}")
            
            return open_user_id
            
        except httpx.HTTPStatusError as e:
            flush_print(f"❌ 开放用户信息接口HTTP错误：状态码 {e.response.status_code}")
            flush_print(f"📄 错误响应：{e.response.text}")
            return None
        except httpx.TimeoutException:
            flush_print("❌ 错误：开放用户信息接口请求超时")
            return None
        except httpx.RequestError as e:
            flush_print(f"❌ 开放用户信息接口请求错误：{str(e)}")
            return None
        except json.JSONDecodeError:
            flush_print("❌ 错误：开放用户信息接口响应不是有效的JSON格式")
            return None
        except Exception as e:
            flush_print(f"❌ 开放用户信息接口未知错误：{str(e)}")
            return None


async def create_joyspace_document(
    title: str,
    content: str,
    open_user_id: str = "default_user",
    open_team_id: str = Open_Team_ID,
    folder_id: str = None,
    team_id: str = None,
    team_access_token: str = None
) -> dict[str, Any] | None:
    """
    创建 JoySpace 文档
    
    Args:
        title: 文档标题
        content: 文档内容
        open_user_id: 开放用户ID
        open_team_id: 开放用户teamId
        folder_id: 文件夹ID
        team_id: 团队ID
        team_access_token: 团队访问令牌（如果提供则不重新获取）
    
    Returns:
        创建结果的字典，失败时返回 None
    """
    # 1、验证输入参数的有效性
    if not title or not title.strip():
        flush_print("❌ 错误：文档标题不能为空")
        return None
    
    if not content or not content.strip():
        flush_print("❌ 错误：文档内容不能为空")
        return None
    
    if not open_user_id:
        flush_print("❌ 错误：开放用户ID不能为空")
        return None
    
    if not open_team_id:
        flush_print("❌ 错误：开放用户teamId不能为空")
        return None
    
    # 2、获取团队访问令牌（如果未提供）
    if not team_access_token:
        # 获取应用访问令牌
        app_access_token = await get_app_access_token()
        if not app_access_token:
            flush_print("❌ 错误：无法获取应用访问令牌")
            return None
        
        # 获取团队访问令牌
        team_access_token = await get_team_access_token(app_access_token, open_team_id)
        if not team_access_token:
            flush_print("❌ 错误：无法获取团队访问令牌")
            return None
    
    # 4、构建HTTP请求头（修复：使用变量而非字符串）
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "authorization": f"Bearer {team_access_token}"
    }
    
    # 5、构建文档创建请求参数
    # 生成JSON字符串格式的content，保持换行符不转义
    # 手动构建content JSON字符串，避免转义换行符
    content_json = f'[{{"value":"{content}"}}]'
    
    payload = {
        "openUserId": open_user_id,
        "openTeamId": Open_Team_ID,
        "pageType": 13,  # 默认文档类型
        "title": title,
        "content": content_json,  # 使用JSON字符串格式
        "contentType": "markdown",  # 固定添加contentType参数
        "scene": SCENE,  # 使用常量定义的场景值
        "teamId": team_id,  # 如果提供，则使用提供的团队ID
        "folderId": folder_id  # 如果提供，则使用提供的文件夹ID
    }

    flush_print(f"🚀 正在创建文档：{title}")
    flush_print(f"📋 请求参数：{json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    # 6、发送HTTP POST请求到JoySpace文档创建接口
    async with httpx.AsyncClient() as client:
        try:
            # 打印请求的入参报文和header信息
            flush_print("\n" + "="*50)
            flush_print("📝 调用 JoySpace createPage 接口")
            flush_print("🌐 接口地址：" + JS_API_BASE)
            flush_print("📋 请求头信息：")
            flush_print(json.dumps(headers, ensure_ascii=False, indent=4))
            flush_print("📦 请求体内容：")
            flush_print(json.dumps(payload, ensure_ascii=False, indent=4))
            flush_print("="*50 + "\n")
            
            # 手动序列化payload以避免双重转义
            payload_json = json.dumps(payload, ensure_ascii=False)
            
            response = await client.post(
                JS_API_BASE,
                headers=headers,
                data=payload_json,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            # 7、检查接口返回结果并处理
            flush_print(f"📄 响应结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查是否创建成功
            if result.get("code") == 0:
                flush_print(f"✅ 成功创建文档：{title}")
                return result
            else:
                flush_print(f"❌ 创建文档失败：{result.get('msg', '未知错误')}")
                return None
            
        except httpx.HTTPStatusError as e:
            flush_print(f"❌ HTTP错误：状态码 {e.response.status_code}")
            flush_print(f"📄 响应内容：{e.response.text}")
            return None
        except httpx.TimeoutException:
            flush_print("❌ 错误：请求超时")
            return None
        except httpx.RequestError as e:
            flush_print(f"❌ 请求错误：{str(e)}")
            return None
        except json.JSONDecodeError:
            flush_print("❌ 错误：响应不是有效的JSON格式")
            return None
        except Exception as e:
            flush_print(f"❌ 未知错误：{str(e)}")
            return None


@mcp.tool()
async def create_document_alert(
    title: str,
    content: str,
    user_id: str = "org.ai.code.review1",
    folder_id: str = None,
    team_id: str = None,
) -> str:
    """Create a JoySpace document using new API and return status message.

    Args:
        title: 文档标题
        content: 文档内容
        user_id: 用户ID，默认为org.ai.code.review1
        folder_id: 文件夹ID
        team_id: 团队ID
        
    """
    
    # 1、验证输入参数的有效性
    if not title or not title.strip():
        error_msg = "错误：文档标题不能为空"
        return error_msg
    
    if not content or not content.strip():
        error_msg = "错误：文档内容不能为空"
        return error_msg
    
    if not user_id or not user_id.strip():
        error_msg = "错误：用户ID不能为空"
        return error_msg
    
    # 2、获取应用访问令牌
    app_access_token = await get_app_access_token()
    if not app_access_token:
        error_msg = "错误：无法获取应用访问令牌，请检查应用配置"
        return error_msg
    
    # 3、获取团队访问令牌
    team_access_token = await get_team_access_token(app_access_token)
    if not team_access_token:
        error_msg = "错误：无法获取团队访问令牌，请检查应用配置"
        return error_msg
    
    # 4、获取开放用户信息
    open_user_id = await get_open_user_info(
        team_access_token=team_access_token,
        user_id=user_id.strip(),
        app_key=APP_KEY
    )
    
    if not open_user_id:
        error_msg = "错误：获取开放用户信息失败，请检查用户ID和团队配置"
        return error_msg
    
    # 5、调用创建文档函数
    result = await create_joyspace_document(
        title=title.strip(),
        content=content.strip(),
        open_user_id=open_user_id,
        open_team_id=Open_Team_ID,
        folder_id=folder_id,
        team_id=team_id,
        team_access_token=team_access_token
    )
    
    # 6、检查文档创建结果并返回相应信息
    if not result:
        error_msg = "错误：创建文档失败，请检查网络连接和参数设置"
        return error_msg
    
    # 7、格式化返回结果 - 修复：检查result是否为None
    if result and result.get("code") == 0:
        # 提取关键信息
        data = result.get('data', {})
        document_url = data.get('url', '未知')
        document_id = data.get('id', '未知')
        created_at = data.get('createdAt', data.get('createTime', '未知'))
        
        # 构建成功信息，重点突出URL
        success_info = f"""✅ 文档创建成功！
📄 标题: {title}

🔗 访问链接: {document_url}

📄 文档ID: {document_id}
👤 用户ID: {user_id}
🆔 开放用户ID: {open_user_id}
🏢 团队ID: {Open_Team_ID}
⏰ 创建时间: {created_at}"""
        
        # 添加可选参数信息
        if folder_id:
            success_info += f"\n📁 文件夹ID: {folder_id}"
        
        if team_id:
            success_info += f"\n👥 指定团队ID: {team_id}"
        
        return success_info
    else:
        # 处理创建失败的情况
        error_msg = "未知错误"
        error_code = "未知"
        
        if result:
            error_msg = result.get('msg', '未知错误')
            error_code = result.get('code', '未知')
        
        # 构建详细失败信息
        failure_info = f"""❌ 文档创建失败！
📄 标题: {title}

🚫 错误代码: {error_code}
❌ 错误信息: {error_msg}

📋 详细信息:
👤 用户ID: {user_id}
🆔 开放用户ID: {open_user_id}
🏢 团队ID: {Open_Team_ID}"""
        
        # 添加可选参数信息
        if folder_id:
            failure_info += f"\n📁 文件夹ID: {folder_id}"
        
        if team_id:
            failure_info += f"\n👥 指定团队ID: {team_id}"
        
        # 添加诊断建议
        failure_info += f"""

💡 诊断建议:
• 检查用户权限配置
• 验证团队ID和文件夹ID是否正确
• 确认网络连接正常
• 联系管理员获取帮助"""
        
        return failure_info


async def interactive_mode():
    """交互式模式 - 允许用户直接操作文档创建功能"""
    flush_print("🎉 欢迎使用 JoySpace 文档创建工具！")
    flush_print("=" * 50)
    
    while True:
        flush_print("\n📋 请选择操作：")
        flush_print("1. 创建新文档")
        flush_print("2. 启动 MCP 服务器模式")
        flush_print("3. 退出程序")
        
        try:
            choice = input("\n请输入选项 (1-3): ").strip()
            
            if choice == "1":
                await create_document_interactive()
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


async def create_document_interactive():
    """交互式创建文档"""
    flush_print("\n📝 创建新文档")
    flush_print("-" * 30)
    
    try:
        title = input("请输入文档标题: ").strip()
        if not title:
            flush_print("❌ 标题不能为空")
            return
            
        content = input("请输入文档内容: ").strip()
        if not content:
            flush_print("❌ 内容不能为空")
            return
            
        user_id = input("请输入用户ID (默认: default_user): ").strip()
        if not user_id:
            user_id = "default_user"
            
            
        # 添加可选参数：folder_id 和 team_id
        folder_id = input("请输入文件夹ID (可选，直接回车跳过): ").strip()
        if not folder_id:
            folder_id = None
            
        team_id = input("请输入团队ID (可选，直接回车跳过): ").strip()
        if not team_id:
            team_id = None
        
        flush_print("\n🚀 开始创建文档...")
        result = await create_joyspace_document(
            title=title,
            content=content,
            open_user_id=user_id,
            folder_id=folder_id,
            team_id=team_id
        )
        
        if result:
            flush_print("\n🎉 文档创建成功！")
        else:
            flush_print("\n❌ 文档创建失败")
            
    except KeyboardInterrupt:
        flush_print("\n⏹️ 操作已取消")
    except Exception as e:
        flush_print(f"\n❌ 发生错误：{str(e)}")


def show_help():
    """显示帮助信息"""
    flush_print("""
🎯 JoySpace 文档创建工具使用说明

运行模式：
  uv run design.py                    # 交互式模式
  uv run design.py --mcp             # 直接启动 MCP 服务器
  uv run design.py --help            # 显示帮助信息

交互式模式功能：
  1. 创建新文档 - 通过交互式界面创建文档
  2. 启动 MCP 服务器 - 切换到 MCP 服务器模式
  3. 退出程序

MCP 服务器模式：
  - 通过 stdio 传输运行
  - 等待 MCP 客户端连接
  - 提供 create_document_alert 工具
""")




def main_sync():
    """同步主函数，处理 MCP 服务器启动"""
    flush_print("🔧 JoySpace 文档创建工具启动中...")
    
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