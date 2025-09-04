#!/usr/bin/env python3
"""简化的API测试，尝试不同的方法"""

import asyncio
import json
import httpx

API_URL = "https://api.tu-zi.com/v1/chat/completions"
API_KEY = "sk-pYZdmlGyl98eYE8MWLIEgQNmCFM6gqkiTd6gMc4UNIJp8nxb"
MODEL_NAME = "gemini-2.5-flash-image"

async def test_non_stream():
    """测试非流式请求"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "test-script/1.0"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": "一只可爱的小猫"
            }
        ],
        "stream": False  # 非流式
    }
    
    print("Testing non-streaming request...")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(API_URL, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

async def test_stream_with_timeout():
    """测试流式请求但使用更长的超时"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "test-script/1.0"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": "一只可爱的小猫"
            }
        ],
        "stream": True
    }
    
    print("Testing streaming request with longer timeout...")
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            full_response = ""
            chunk_count = 0
            
            async with client.stream('POST', API_URL, headers=headers, json=payload) as response:
                print(f"Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error: {error_text.decode()}")
                    return
                
                async for chunk in response.aiter_lines():
                    chunk_count += 1
                    
                    if chunk_count % 100 == 0:
                        print(f"Processed {chunk_count} chunks...")
                    
                    if chunk.startswith('data: '):
                        if chunk == 'data: [DONE]':
                            print("Received [DONE] signal")
                            break
                        try:
                            data = json.loads(chunk[6:])
                            if (data.get("choices") and 
                                len(data["choices"]) > 0 and
                                data["choices"][0].get("delta") and 
                                data["choices"][0]["delta"].get("content")):
                                content = data["choices"][0]["delta"]["content"]
                                full_response += content
                        except json.JSONDecodeError:
                            continue
                    
                    # 超过5000块就停止（可能有问题）
                    if chunk_count > 5000:
                        print("Stopping after 5000 chunks")
                        break
                
                print(f"Total chunks: {chunk_count}")
                print(f"Full Response length: {len(full_response)}")
                print("Last 500 characters of response:")
                print(full_response[-500:] if len(full_response) > 500 else full_response)
                
                # 查找图片URL
                import re
                urls = re.findall(r'https?://[^\s"\']+', full_response)
                if urls:
                    print(f"Found URLs: {urls}")
                else:
                    print("No URLs found")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    print("=== Testing Non-Stream API ===")
    await test_non_stream()
    
    print("\n=== Testing Stream API with Timeout ===")
    await test_stream_with_timeout()

if __name__ == "__main__":
    asyncio.run(main())