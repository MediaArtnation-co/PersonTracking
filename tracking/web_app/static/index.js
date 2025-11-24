// index.js

document.addEventListener("DOMContentLoaded", () => {
    const videoStream = document.getElementById("videoStream");
    
    // WebSocket URL 구성 (ws:// 또는 wss:// 사용)
    const protocol = location.protocol === "https:" ? "wss://" : "ws://";
    const url = protocol + location.host + "/ws/video";

    const ws = new WebSocket(url);
    
    ws.binaryType = "arraybuffer"; // 바이너리 데이터 수신 설정

    ws.onopen = () => {
        console.log("🔌 서버와 WebSocket 연결 성공. 스트림 수신 시작.");
    };

    ws.onmessage = (event) => {
        // 서버에서 JPEG 바이트 데이터를 받으면
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        
        // Blob 데이터를 URL로 변환하여 <img> 태그에 할당 (이미지 출력)
        const imageUrl = URL.createObjectURL(blob);
        videoStream.src = imageUrl;
        
        // 메모리 해제
        videoStream.onload = () => {
            URL.revokeObjectURL(imageUrl);
        };
    };

    ws.onclose = () => {
        console.log("🔌 연결 종료됨. 스트림이 중단되었습니다.");
    };

    ws.onerror = (e) => {
        console.error("WS 오류:", e);
    };
});