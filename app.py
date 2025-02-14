from fastapi import Body, FastAPI, Request, WebSocketDisconnect
from fastapi.websockets import WebSocket
import uuid
from auth import *
from db import *

app = FastAPI()

@app.post("/users/register")
def post_user(data = Body()):
    return register_user(data["login"], data["nickname"], data["group"], data["password"])

@app.post("/users/login")
def l_user(data = Body()):
    return login_user(data["login"],data["password"])

@app.get("/users/account")
def get_user(request : Request):
    return get_account_user(get_user_id(request))

@app.post("/chats/create")
def post_chat(request : Request, data = Body()):
    create_chat(data["name"], get_user_id(request))
    
@app.get("/chats/{chatId}")
def get_chat(chatId : uuid.UUID,request : Request):
    return read_chat(chatId, get_user_id(request))

rooms : dict[uuid.UUID,list[WebSocket]] = {}
@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: uuid.UUID):
    user_id = get_user_id(websocket)
    await websocket.accept()

    if(chat_id in rooms.keys()):    rooms[chat_id].append(websocket)
    else:   rooms[chat_id] = [websocket]

    try:
        while True:
            data = await websocket.receive_text()

            m_id = create_message(data, user_id, chat_id)
            message = read_message(m_id)

            for u in rooms[chat_id]:
                await u.send_text(message)
    except WebSocketDisconnect:
        rooms[chat_id].remove(websocket)

    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)