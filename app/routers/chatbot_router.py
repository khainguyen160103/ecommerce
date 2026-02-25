"""
Chatbot Router - WebSocket endpoint cho chatbot AI
Hỗ trợ streaming response
"""
import json
import traceback
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from app.services.chatbot_service import chatbot_service

chatbotRouter = APIRouter(tags=["Chatbot"])


@chatbotRouter.websocket("/chat/ws")
async def chat_websocket(websocket: WebSocket):
    """
    WebSocket endpoint cho chatbot.
    
    Client gửi JSON:
    {
        "message": "Xin chào",
        "history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    
    Server trả về JSON stream:
    {"type": "chunk", "content": "Xin "}
    {"type": "chunk", "content": "chào "}
    {"type": "chunk", "content": "bạn!"}
    {"type": "done"}
    
    Hoặc lỗi:
    {"type": "error", "content": "..."}
    """
    await websocket.accept()
    
    try:
        while True:
            # Nhận message từ client
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                message = payload.get("message", "").strip()
                history = payload.get("history", [])
                
                if not message:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Vui lòng nhập tin nhắn"
                    })
                    continue
                
                # Giới hạn history 10 cặp gần nhất (tiết kiệm token)
                if len(history) > 20:
                    history = history[-20:]
                
                # Tạo session cho mỗi request
                from app.core.database import engine
                with Session(engine) as session:
                    # Stream response
                    async for chunk in chatbot_service.stream_chat(
                        message=message,
                        history=history,
                        session=session,
                    ):
                        await websocket.send_json({
                            "type": "chunk",
                            "content": chunk
                        })
                
                # Báo hiệu đã xong
                await websocket.send_json({"type": "done"})
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "content": "Invalid JSON format"
                })
            except Exception:
                traceback.print_exc()
                await websocket.send_json({
                    "type": "error",
                    "content": "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại."
                })
                
    except WebSocketDisconnect:
        print("Client disconnected from chatbot")
    except Exception:
        traceback.print_exc()
        try:
            await websocket.close()
        except Exception:
            pass
