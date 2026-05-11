import os
import sys
import subprocess
import threading
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

app = FastAPI(title="Temu Profit Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STREAMLIT_PORT = 8501
STREAMLIT_URL = f"http://127.0.0.1:{STREAMLIT_PORT}"
streamlit_process = None
is_streamlit_ready = False


def start_streamlit():
    global streamlit_process, is_streamlit_ready
    
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(STREAMLIT_PORT),
        "--server.address", "127.0.0.1",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--logger.level", "warning"
    ]
    
    print(f"🚀 Starting Streamlit: {' '.join(streamlit_cmd)}")
    
    streamlit_process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )
    
    max_wait = 30
    wait_interval = 0.5
    
    for i in range(int(max_wait / wait_interval)):
        try:
            response = httpx.get(STREAMLIT_URL, timeout=2)
            if response.status_code == 200:
                is_streamlit_ready = True
                print("✅ Streamlit is ready!")
                return True
        except:
            pass
        
        time.sleep(wait_interval)
        
        if i % 10 == 0 and i > 0:
            print(f"⏳ Waiting for Streamlit... ({i * wait_interval:.1f}s)")
    
    print("❌ Streamlit failed to start within timeout")
    return False


threading.Thread(target=start_streamlit, daemon=True).start()


@app.get("/health")
async def health_check():
    return {"status": "ok", "streamlit_ready": is_streamlit_ready}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_to_streamlit(request: Request, path: str):
    if not is_streamlit_ready:
        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Temu 利润管家 - 启动中...</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .container {
                        text-align: center;
                        padding: 3rem;
                        background: rgba(255,255,255,0.95);
                        border-radius: 20px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                        max-width: 500px;
                    }
                    .spinner {
                        width: 50px;
                        height: 50px;
                        border: 5px solid #f3f3f3;
                        border-top: 5px solid #FF6B35;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 20px auto;
                    }
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    h1 { color: #333; margin-bottom: 1rem; }
                    p { color: #666; line-height: 1.6; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="spinner"></div>
                    <h1>🚀 Temu 利润管家</h1>
                    <p>应用正在启动中，请稍候...</p>
                    <p style="font-size: 0.9rem; color: #999; margin-top: 2rem;">
                        首次启动可能需要 30-60 秒<br>
                        请刷新页面重试
                    </p>
                </div>
                <script>setTimeout(() => location.reload(), 3000)</script>
            </body>
            </html>
            """,
            status_code=503
        )

    try:
        url = f"{STREAMLIT_URL}/{path}" if path else STREAMLIT_URL
        
        params = dict(request.query_params)
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                params=params,
                headers=headers,
                content=body,
            )
            
            excluded_headers = [
                'content-encoding',
                'content-length',
                'transfer-encoding',
                'connection'
            ]
            
            response_headers = [
                (k, v) for k, v in response.headers.items()
                if k.lower() not in excluded_headers
            ]
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response_headers)
            )
            
    except Exception as e:
        print(f"❌ Proxy error: {str(e)}")
        return HTMLResponse(
            content=f"<h1>Proxy Error</h1><p>{str(e)}</p>",
            status_code=500
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)