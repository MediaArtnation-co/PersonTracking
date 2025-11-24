# main.py

from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import HTMLResponse

# YOLO 처리 로직 임포트
from yolo_stream import video_processing_generator 

# 현재는 비디오 파일을 사용하지만, 필요 시 경로를 외부 변수로 변경 가능
VIDEO_PATH = "video1.mp4"
# VIDEO_PATH = 0

# ==================== FastAPI 초기 설정 ====================
BASE_DIR = Path(__file__).parent
app = FastAPI(title="YOLO Live Stream Server")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ==================== 라우팅 ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket 연결 수락: YOLO 스트림 시작")
    
    try:
        # 비디오 제너레이터 시작
        frame_generator = video_processing_generator(VIDEO_PATH)
        
        # 제너레이터에서 프레임을 하나씩 받아 WebSocket으로 전송
        for jpeg_bytes in frame_generator:
            await websocket.send_bytes(jpeg_bytes)
            # 프레임 전송 속도를 조절해야 할 경우 (CPU 부하 경감)
            # await asyncio.sleep(0.01) 
            
    except Exception as e:
        print(f"❌ WebSocket 전송 오류 발생: {e}")
        
    finally:
        print("🔌 WebSocket 연결 종료")
        await websocket.close()

# =========================================================
# 실행: uvicorn main:app --reload