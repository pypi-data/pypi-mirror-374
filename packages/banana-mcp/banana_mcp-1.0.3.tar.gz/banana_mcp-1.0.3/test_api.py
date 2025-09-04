#!/usr/bin/env python3
"""测试Gemini API直接响应"""

import asyncio
import json
import httpx

API_URL = "https://api.tu-zi.com/v1/chat/completions"
API_KEY = "sk-pYZdmlGyl98eYE8MWLIEgQNmCFM6gqkiTd6gMc4UNIJp8nxb"
MODEL_NAME = "gemini-2.5-flash-image"

async def test_api():
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
                "content": "一只威猛的白虎正在抓捕一只小鸡"
            }
        ],
        "stream": True
    }
    
    print("Sending request to API...")
    print(f"URL: {API_URL}")
    print(f"Model: {MODEL_NAME}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\n" + "="*80 + "\n")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            full_response = ""
            async with client.stream('POST', API_URL, headers=headers, json=payload) as response:
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print("\n" + "="*80 + "\n")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error: {error_text.decode()}")
                    return
                
                print("Streaming response chunks:")
                chunk_count = 0
                
                async for chunk in response.aiter_lines():
                    chunk_count += 1
                    print(f"Chunk {chunk_count}: {chunk[:200]}..." if len(chunk) > 200 else f"Chunk {chunk_count}: {chunk}")
                    
                    if chunk.startswith('data: '):
                        if chunk == 'data: [DONE]':
                            print("  -> Received [DONE] signal")
                            break
                        try:
                            data = json.loads(chunk[6:])
                            if (data.get("choices") and 
                                len(data["choices"]) > 0 and
                                data["choices"][0].get("delta") and 
                                data["choices"][0]["delta"].get("content")):
                                content = data["choices"][0]["delta"]["content"]
                                full_response += content
                                print(f"  -> Content: {content[:100]}..." if len(content) > 100 else f"  -> Content: {content}")
                        except json.JSONDecodeError as e:
                            print(f"  -> JSON decode error: {e}")
                    
                    # 如果超过1000个块，停止（防止无限循环）
                    if chunk_count > 1000:
                        print("Stopping after 1000 chunks to prevent infinite loop")
                        break
                
                print("\n" + "="*80 + "\n")
                print(f"Full Response (length: {len(full_response)}):")
                print(full_response[:1000] + "..." if len(full_response) > 1000 else full_response)
                
                # 查找图片URL
                print("\n" + "="*80 + "\n")
                print("Searching for image URLs...")
                
                import re
                
                # 各种URL模式
                url_patterns = [
                    r'https?://[^\s"\'<>\[\]{}()]*\.(?:jpg|jpeg|png|gif|webp|bmp)',
                    r'"(?:url|image|image_url|data_url)"\s*:\s*"(https?://[^"]+)"',
                    r'https?://[^\s"\']*'
                ]
                
                found_urls = []
                for pattern in url_patterns:
                    matches = re.findall(pattern, full_response, re.IGNORECASE)
                    if matches:
                        found_urls.extend(matches)
                
                if found_urls:
                    print(f"Found {len(found_urls)} potential URLs:")
                    for i, url in enumerate(found_urls[:5], 1):
                        print(f"  {i}. {url}")
                else:
                    print("No URLs found in response")
                
                # 查找JSON对象
                print("\n" + "="*80 + "\n")
                print("Searching for JSON objects...")
                
                json_pattern = r'\{[^{}]*\}'
                json_matches = re.findall(json_pattern, full_response)
                
                if json_matches:
                    print(f"Found {len(json_matches)} potential JSON objects:")
                    for i, obj_str in enumerate(json_matches[:3], 1):
                        print(f"  Object {i}: {obj_str[:200]}..." if len(obj_str) > 200 else f"  Object {i}: {obj_str}")
                        try:
                            obj = json.loads(obj_str)
                            print(f"    -> Valid JSON: {obj}")
                        except:
                            print(f"    -> Invalid JSON")
                else:
                    print("No JSON objects found")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())