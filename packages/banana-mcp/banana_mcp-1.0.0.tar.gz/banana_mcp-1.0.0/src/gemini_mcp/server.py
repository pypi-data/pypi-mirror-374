#!/usr/bin/env python3
"""
Gemini MCP Server

MCP server for generating images using Gemini 2.5 Flash via the tu-zi.com API.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
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
        
        # 返回结果
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        # 返回错误信息
        error_result = {
            "success": False,
            "error": str(e),
            "message": "❌ 图片生成失败",
            "timestamp": get_current_timestamp(),
            "service": "Gemini 2.5 Flash Image Generation (Python MCP Package)"
        }
        return [
            TextContent(
                type="text", 
                text=json.dumps(error_result, indent=2, ensure_ascii=False)
            )
        ]

async def generate_image_with_gemini(prompt: str, api_key: str) -> Dict[str, Any]:
    """调用Gemini API生成图片"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "gemini-mcp/1.0.0"
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
                
                # 尝试提取图片数据
                try:
                    import re
                    json_match = re.search(r'\{[^}]*"model"[^}]*\}', result)
                    if json_match:
                        image_data = json.loads(json_match.group())
                except Exception as e:
                    logger.debug(f"Could not extract image data: {e}")
                
                return {
                    "success": True,
                    "prompt": prompt,
                    "response": result,
                    "imageData": image_data,
                    "message": "🎨 图片生成完成！结果中包含图片相关信息",
                    "timestamp": get_current_timestamp(),
                    "service": "Gemini 2.5 Flash Image Generation (Python MCP Package)",
                    "model": MODEL_NAME,
                    "version": "1.0.0"
                }
                
        except httpx.TimeoutException:
            raise Exception("请求超时，请稍后重试")
        except httpx.RequestError as e:
            raise Exception(f"网络请求错误: {str(e)}")

def get_current_timestamp() -> str:
    """获取当前时间戳"""
    from datetime import datetime
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