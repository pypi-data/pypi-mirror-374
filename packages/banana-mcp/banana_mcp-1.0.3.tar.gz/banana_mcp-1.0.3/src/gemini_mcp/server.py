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
                success_message += f"\n💾 图片已保存到: {result['saved_path']}"
            else:
                success_message += f"\n⚠️ 图片生成成功但未能保存到本地（可能API返回格式不包含图片数据）"
                
            success_message += f"\n🤖 服务: {result.get('service', 'Gemini 2.5 Flash')}"
            
            # 如果有原始响应，显示最后一部分（通常包含图片URL）
            if result.get('response'):
                response_length = len(result['response'])
                if response_length > 400:
                    # 显示最后400个字符，通常包含图片信息
                    response_preview = "..." + result['response'][-400:]
                else:
                    response_preview = result['response']
                success_message += f"\n📄 API响应 (长度:{response_length}): {response_preview}"
            
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
        "User-Agent": "banana-mcp/1.0.3"
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
                chunk_count = 0
                
                logger.info("Starting to read streaming response...")
                
                async for chunk in response.aiter_lines():
                    chunk_count += 1
                    
                    # 记录所有非空响应块
                    if chunk.strip():
                        logger.debug(f"Chunk {chunk_count}: {chunk[:100]}..." if len(chunk) > 100 else f"Chunk {chunk_count}: {chunk}")
                    
                    # 处理SSE数据块
                    if chunk.startswith('data: '):
                        if chunk == 'data: [DONE]':
                            logger.info("Received [DONE] signal, ending stream")
                            break
                            
                        try:
                            data = json.loads(chunk[6:])
                            if (data.get("choices") and 
                                len(data["choices"]) > 0 and
                                data["choices"][0].get("delta") and 
                                data["choices"][0]["delta"].get("content")):
                                content = data["choices"][0]["delta"]["content"]
                                result += content
                                logger.debug(f"Added content: {content[:50]}..." if len(content) > 50 else f"Added content: {content}")
                        except json.JSONDecodeError as e:
                            logger.debug(f"JSON decode error for chunk: {e}")
                            continue
                
                logger.info(f"Finished reading stream. Total chunks: {chunk_count}, Response length: {len(result)}")
                logger.debug(f"Full response: {result[:500]}..." if len(result) > 500 else f"Full response: {result}")
                
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
                    "version": "1.0.3"
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
    
    logger.info(f"Searching for image in API response (length: {len(api_response)})")
    
    # 尝试从响应中提取图片URL或base64数据
    image_url = None
    base64_data = None
    
    # 查找图片URL (专门匹配这个API的格式)
    url_patterns = [
        # 匹配Markdown图片格式: ![alt](url)
        r'!\[.*?\]\((https?://[^)]+)\)',
        # 匹配带有cdn、img、images等关键词的URL
        r'https?://[^\s"\'<>\[\]{}()]*(?:cdn|img|images?|photo|picture|ffire)[^\s"\'<>\[\]{}()]*',
        # 匹配以常见图片扩展名结尾的URL
        r'https?://[^\s"\'<>\[\]{}()]*\.(?:jpg|jpeg|png|gif|webp|bmp)(?:\?[^\s"\'<>\[\]{}()]*)?',
        # 匹配JSON中的URL字段
        r'"(?:url|image|image_url|data_url)"\s*:\s*"(https?://[^"]+)"',
        # 匹配任何看起来像图片服务的URL
        r'https?://[^\s"\']*s3[^\s"\']*',
        r'https?://[^\s"\']*imgur[^\s"\']*',
        r'https?://[^\s"\']*cloudinary[^\s"\']*'
    ]
    
    for i, pattern in enumerate(url_patterns):
        matches = re.findall(pattern, api_response, re.IGNORECASE)
        if matches:
            logger.info(f"Found {len(matches)} URLs with pattern {i} ({pattern}): {matches[:3]}")
            for match in matches:
                if isinstance(match, tuple):
                    # 对于带组的匹配，取第一个组
                    potential_url = match[0] if match[0] else (match[1] if len(match) > 1 else str(match))
                else:
                    potential_url = str(match)
                
                # 清理URL - 移除尾部的特殊字符
                potential_url = re.sub(r'[)>\]}\s]*$', '', potential_url)
                
                if potential_url and 'http' in potential_url and len(potential_url) > 10:
                    image_url = potential_url
                    logger.info(f"Selected image URL: {image_url}")
                    break
            if image_url:
                break
    
    # 查找base64数据 (更多模式)
    base64_patterns = [
        r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)',
        r'"(?:image|data|base64)"\s*:\s*"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)"',
        r'"(?:image|data|base64)"\s*:\s*"([A-Za-z0-9+/=]{100,})"',
        r'base64["\']?\s*:\s*["\']?([A-Za-z0-9+/=]{100,})["\']?',
        r'([A-Za-z0-9+/=]{500,})'  # 长base64字符串
    ]
    
    for i, pattern in enumerate(base64_patterns):
        matches = re.findall(pattern, api_response)
        if matches:
            logger.info(f"Found {len(matches)} base64 patterns with pattern {i}")
            base64_data = matches[0]
            if isinstance(base64_data, tuple):
                base64_data = base64_data[0]
            break
    
    # 如果没找到标准格式，尝试直接从响应中提取任何看起来像图片的内容
    if not image_url and not base64_data:
        # 查找任何包含图片相关关键词的URL
        general_url_match = re.search(r'(https?://[^\s"\']+)', api_response)
        if general_url_match:
            potential_url = general_url_match.group(1)
            logger.info(f"Found potential URL: {potential_url}")
            # 检查这个URL是否可能是图片
            if any(ext in potential_url.lower() for ext in ['.jpg', '.png', '.gif', '.webp', '.jpeg']):
                image_url = potential_url
    
    if not image_url and not base64_data:
        logger.warning("No image URL or base64 data found in response")
        logger.debug(f"Response snippet: {api_response[:500]}...")
        return None
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = re.sub(r'[^\w\s-]', '', prompt[:30]).strip()
    safe_prompt = re.sub(r'[-\s]+', '_', safe_prompt)
    filename = f"gemini_{timestamp}_{safe_prompt}.png"
    file_path = base_path / filename
    
    try:
        if image_url:
            logger.info(f"Attempting to download image from URL: {image_url}")
            # 下载图片
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Image successfully saved from URL to: {file_path}")
                    return str(file_path)
                else:
                    logger.error(f"Failed to download image: HTTP {response.status_code}")
        
        elif base64_data:
            logger.info(f"Attempting to save base64 image (length: {len(base64_data)})")
            # 保存base64图片
            try:
                # 如果base64数据不以标准padding结尾，补充padding
                missing_padding = len(base64_data) % 4
                if missing_padding:
                    base64_data += '=' * (4 - missing_padding)
                
                image_bytes = base64.b64decode(base64_data)
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                logger.info(f"Image successfully saved from base64 to: {file_path}")
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