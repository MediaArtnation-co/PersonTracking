# yolo_stream.py

import cv2
from ultralytics import YOLO
import numpy as np
import time

# Load the YOLO11 model (모델은 한 번만 로드)
# 전역 변수로 선언하여 루프마다 로드하지 않도록 합니다.
model = YOLO("yolo11n.pt")
# 추적 기능을 위해 persist=True를 유지
tracker_args = dict(
    classes=[0],
    conf=0.5,
    max_det=10,
    tracker="bytetrack.yaml",
    persist=True
)


def video_processing_generator(video_path):
    """
    비디오 파일을 처리하고 시각화된 JPEG 프레임을 yield하는 제너레이터
    """
    cap = cv2.VideoCapture(video_path)
    prev_time = 0 
    
    print("\n=======================================================")
    print("           YOLO Tracking Console Log Started")
    print("=======================================================")

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        # FPS 계산
        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time 
        fps_text = f"FPS: {fps:.2f}" 

        # YOLO 추적 실행
        results = model.track(frame, **tracker_args)
        
        # 2. Visualize (바운딩 박스)
        annotated_frame = results[0].plot()

        # 3. 객체 중심점 및 ID 추출/오버레이 (영상 출력 로직)
        boxes = results[0].boxes
        box_data = boxes.xyxy.cpu().numpy()
        
        # 추적 ID 데이터
        if boxes.id is not None:
            track_ids = boxes.id.cpu().numpy().astype(int)
        else:
            track_ids = []

        
        # --------------------------------------------------------
        # 🔥 콘솔 출력 로직 추가
        # --------------------------------------------------------
        print(f"\n[{fps_text}] - Detected Objects: {len(box_data)}")
        
        if len(box_data) > 0:
            for i, box in enumerate(box_data):
                x1, y1, x2, y2 = map(int, box[:4])
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                current_id = track_ids[i] if len(track_ids) > i else "N/A"
                
                # 객체 정보 콘솔 출력
                print(f"  > ID: {current_id:<3} | Center X, Y: ({center_x:<4}, {center_y:<4}) | BBox: ({x1}, {y1}) to ({x2}, {y2})")

                # --- 영상 오버레이 (기존 로직 유지) ---
                cv2.circle(annotated_frame, (center_x, center_y), 5, (0, 0, 255), -1)
                coord_text = f"({center_x}, {center_y})"
                cv2.putText(annotated_frame, coord_text, (center_x + 10, center_y + 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        # --------------------------------------------------------
        
        # 4. FPS 텍스트 (빨간색)
        cv2.putText(annotated_frame, fps_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        # 5. 프레임을 JPEG로 인코딩하여 전송 준비
        (flag, encoded_image) = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        
        if flag:
            yield encoded_image.tobytes() 

        prev_time = current_time
    
    cap.release()
    print("=======================================================")
    print("               Video Stream Processing Ended")
    print("=======================================================")