import json
import aiohttp
import asyncio

async def test_streaming():
    url = "https://your-railway-url.up.railway.app/api/agency-streaming"
    headers = {
        "Authorization": "Bearer YOUR_APP_TOKEN",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # Test cases
    test_requests = [
        # Basic message without any optional parameters
        {
            "message": "Write a 1000 word poem",
            "description": "Basic message test"
        },
    ]

    async with aiohttp.ClientSession() as session:
        for i, request_data in enumerate(test_requests, 1):
            description = request_data.pop("description")
            print(f"\n=== Test Case {i}: {description} ===")
            print("Request:", json.dumps(request_data, indent=2))
            
            try:
                async with session.post(url, json=request_data, headers=headers) as response:
                    print(f"Status: {response.status}")
                    
                    async for chunk in response.content:
                        if not chunk:  # Connection closed by server
                            print("\nConnection closed by server")
                            break
                        
                        # Print chunk immediately, use end='' to avoid newlines
                        chunk = chunk.decode('utf-8')
                        if not chunk.startswith('data: '):
                            continue
                        
                        chunk_data = json.loads(chunk.replace('data: ', '').strip())
                        text = ''  # Initialize text variable
                        if 'error' in chunk_data:
                            print(chunk_data)
                            break
                        if 'delta' in chunk_data["data"]:
                            content = chunk_data['data']['delta'].get('content', [])
                            text = ''.join(block['text']['value'] for block in content if block['type'] == 'text')
                            if text:
                                print(text, end='', flush=True)
                                
            except aiohttp.ClientConnectionError:
                print("Connection closed by server")
            except Exception as e:
                print(f"Error during streaming: {e}")
            
if __name__ == "__main__":
    print("Starting streaming tests...")
    asyncio.run(test_streaming()) 