#!/usr/bin/env python3
"""
Gemini MCP Server

MCP server for generating images using Gemini 2.5 Flash via the tu-zi.com API.
"""

import asyncio
import json
import os
import sys
import base64
import re
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import logging

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource
)
import mcp.types as types

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器实例
server = Server("gemini-image-generator")

# API配置
API_BASE_URL = "https://api.tu-zi.com/v1/chat/completions"
DEFAULT_API_KEY = "sk-pYZdmlGyl98eYE8MWLIEgQNmCFM6gqkiTd6gMc4UNIJp8nxb"
MODEL_NAME = "gemini-2.5-flash-image"

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """返回可用的工具列表"""
    return [
        Tool(
            name="generate_image",
            description="使用Gemini 2.5 Flash生成图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "图片描述提示词，详细描述想要生成的图片内容"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "API密钥，如果未提供则使用环境变量GEMINI_API_KEY"
                    }
                },
                "required": ["prompt"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """处理工具调用"""
    if name != "generate_image":
        raise ValueError(f"Unknown tool: {name}")
    
    # 获取参数
    prompt = arguments.get("prompt")
    if not prompt:
        raise ValueError("prompt is required")
    
    # 获取API密钥（优先级：参数 > 环境变量 > 默认值）
    api_key = (
        arguments.get("api_key") or 
        os.environ.get("GEMINI_API_KEY") or 
        DEFAULT_API_KEY
    )
    
    logger.info(f"Generating image with prompt: {prompt[:50]}...")
    
    try:
        # 调用图片生成API
        result = await generate_image_with_gemini(prompt, api_key)
        
        if result.get("success", False):
            # 成功时返回清晰的成功信息
            success_message = f"✅ 图片生成成功！\n\n📝 提示词: {prompt}\n⏰ 时间: {result.get('timestamp', '')}"
            if result.get('saved_path'):
                success_message += f"\n💾 保存路径: {result['saved_path']}"
            success_message += f"\n🤖 服务: {result.get('service', 'Gemini 2.5 Flash')}"
            
            return [
                TextContent(
                    type="text",
                    text=success_message
                )
            ]
        else:
            # 失败时返回错误信息
            return [
                TextContent(
                    type="text",
                    text=f"❌ 图片生成失败: {result.get('error', '未知错误')}"
                )
            ]
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        return [
            TextContent(
                type="text", 
                text=f"❌ 图片生成失败: {str(e)}"
            )
        ]

async def generate_image_with_gemini(prompt: str, api_key: str) -> Dict[str, Any]:
    """调用Gemini API生成图片"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "banana-mcp/1.0.1"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": True
    }
    
    timeout = httpx.Timeout(60.0)  # 60秒超时
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            async with client.stream('POST', API_BASE_URL, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise Exception(f"API请求失败: {response.status_code} - {error_text.decode()}")
                
                result = ""
                image_data = None
                
                async for chunk in response.aiter_lines():
                    if chunk.startswith('data: ') and chunk != 'data: [DONE]':
                        try:
                            data = json.loads(chunk[6:])
                            if (data.get("choices") and 
                                len(data["choices"]) > 0 and
                                data["choices"][0].get("delta") and 
                                data["choices"][0]["delta"].get("content")):
                                result += data["choices"][0]["delta"]["content"]
                        except json.JSONDecodeError:
                            continue
                
                # 尝试提取和保存图片
                saved_path = None
                try:
                    saved_path = await extract_and_save_image(result, prompt)
                except Exception as e:
                    logger.warning(f"Could not save image: {e}")
                
                return {
                    "success": True,
                    "prompt": prompt,
                    "response": result,
                    "saved_path": saved_path,
                    "message": "🎨 图片生成完成！",
                    "timestamp": get_current_timestamp(),
                    "service": "Banana MCP - Gemini 2.5 Flash Image Generation",
                    "model": MODEL_NAME,
                    "version": "1.0.1"
                }
                
        except httpx.TimeoutException:
            raise Exception("请求超时，请稍后重试")
        except httpx.RequestError as e:
            raise Exception(f"网络请求错误: {str(e)}")

async def extract_and_save_image(api_response: str, prompt: str) -> Optional[str]:
    """从API响应中提取图片并保存到本地"""
    
    # 获取保存路径
    base_path = os.environ.get("BANANA_MCP_BASE_PATH", ".")
    base_path = Path(base_path)
    
    # 确保目录存在
    base_path.mkdir(parents=True, exist_ok=True)
    
    # 尝试从响应中提取图片URL或base64数据
    image_url = None
    base64_data = None
    
    # 查找图片URL (常见模式)
    url_patterns = [
        r'https?://[^\s]*\.(?:jpg|jpeg|png|gif|webp)',
        r'"url"\s*:\s*"(https?://[^"]+)"',
        r'"image"\s*:\s*"(https?://[^"]+)"',
        r'"image_url"\s*:\s*"(https?://[^"]+)"'
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, api_response, re.IGNORECASE)
        if match:
            if match.groups():
                image_url = match.group(1)
            else:
                image_url = match.group()
            break
    
    # 查找base64数据
    base64_patterns = [
        r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)',
        r'"image"\s*:\s*"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)"',
        r'base64["\']?\s*:\s*["\']?([A-Za-z0-9+/=]+)["\']?'
    ]
    
    for pattern in base64_patterns:
        match = re.search(pattern, api_response)
        if match:
            base64_data = match.group(1)
            break
    
    if not image_url and not base64_data:
        logger.info("No image URL or base64 data found in response")
        return None
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = re.sub(r'[^\w\s-]', '', prompt[:30]).strip()
    safe_prompt = re.sub(r'[-\s]+', '_', safe_prompt)
    filename = f"gemini_{timestamp}_{safe_prompt}.png"
    file_path = base_path / filename
    
    try:
        if image_url:
            # 下载图片
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Image saved from URL to: {file_path}")
                    return str(file_path)
        
        elif base64_data:
            # 保存base64图片
            try:
                image_bytes = base64.b64decode(base64_data)
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"Image saved from base64 to: {file_path}")
                return str(file_path)
            except Exception as e:
                logger.error(f"Failed to decode base64 image: {e}")
                
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        
    return None

def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().isoformat()

async def run_server():
    """运行MCP服务器"""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Gemini MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-image-generator",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

def main():
    """主入口函数"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()