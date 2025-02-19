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

class Hub:
    def __init__(self):
        self.rooms : dict[uuid.UUID,list[WebSocket]] = {}
    def add_socket(self, room_id : uuid.UUID, websocket : WebSocket) -> None:
        if(room_id in self.rooms.keys()):    
            self.rooms[room_id].append(websocket)
        else:   
            self.rooms[room_id] = [websocket]
    def remove_socket(self, room_id : uuid.UUID, websocket : WebSocket) -> None:
        self.rooms[room_id].remove(websocket)
        if self.rooms[room_id] == []:
            self.rooms.pop(room_id)
    async def sendAllAsync(self, room_id : uuid.UUID, message : str) -> None:
        for u in self.rooms[room_id]:
                await u.send_text(message)

hub = Hub() 
@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: uuid.UUID):
    user_id = get_user_id(websocket)
    await websocket.accept()

    hub.add_socket(chat_id,websocket)

    try:
        while True:
            data = await websocket.receive_text()

            m_id = create_message(data, user_id, chat_id)
            message = read_message(m_id)

            await hub.sendAllAsync(chat_id,message)
    except WebSocketDisconnect:
        hub.remove_socket(chat_id,websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)