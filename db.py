from pony.orm import *
from datetime import datetime
import uuid
from auth import create_access_token
from hash import *

db = Database()

class UserModel(db.Entity):
    id = PrimaryKey(uuid.UUID)
    login = Required(str)
    nickName = Required(str)
    group = Required(str)
    password = Required(str)
    chats = Set("ChatModel")
    messages = Set("MessageModel")
class MessageModel(db.Entity):
    id = PrimaryKey(uuid.UUID)
    text = Required(str)
    user : UserModel = Required(UserModel)
    chat = Required("ChatModel")
    datetime = Required(datetime)
class ChatModel(db.Entity):
    id = PrimaryKey(uuid.UUID)
    name = Required(str)
    users = Set(UserModel)
    messages = Set(MessageModel)

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@db_session
def create_message(text : str, userId : uuid.UUID, chatId : uuid.UUID):
    user = UserModel[userId]
    chat = ChatModel[chatId]
    message = MessageModel(
        id = uuid.uuid4(),
        text = text,
        user = user,
        chat = chat,
        datetime = datetime.now()
    )
    return message.id
@db_session
def read_message(messageId : uuid.UUID):
    message = MessageModel[messageId]
    user = message.user
    return { "text" : message.text, 
            "usernickname" : user.nickName, 
            "usergroup" : user.group, 
            "datetime" : message.datetime}

@db_session
def create_chat(name : str, userId : uuid.UUID):
    user = UserModel[userId]
    ChatModel(
        id = uuid.uuid4(),
        name = name,
        users = [user],
        messages = []
    )
@db_session
def read_chat(id : uuid.UUID, userId : uuid.UUID) -> {str, list, list}:
    chat = ChatModel[id]
    if(chat == None):
        raise Exception("Not found chat") 
    
    user = UserModel[userId]
    
    if(user not in chat.users):
        chat.users.add(user)
    
    #это
    users = [{ "nickname" : u.nickName, "group" : u.group} for u in chat.users]

    # и это - одно и то же
    #users = []
    #for u in chat.users:
        #users.append({ "nickname" : u.nickName, "group" : u.group}) 

    messages = [read_message(m.id) for m in chat.messages]

    return {"name" : chat.name, "users" : users, "messages" : messages}
@db_session
def read_link_chat(id : uuid.UUID):
    chat = ChatModel[id]
    return {"id": chat.id, "name" : chat.name}


@db_session
def register_user(login: str, nickname : str, group : str, password : str):
    tryuser : UserModel = UserModel.get(login = login)
    if(tryuser != None):
        raise Exception("user already exist")
    UserModel(
        id = uuid.uuid4(),
        login = login,
        nickName = nickname,
        group = group,
        password = get_password_hash(password),
        chats = []) 
@db_session
def login_user(login:str,password:str) -> str:
    tryuser : UserModel = UserModel.get(login = login)

    if(tryuser == None):
        raise Exception("User not found")
    
    if(not verify_password(password, tryuser.password)):
        raise Exception("Password incorrect")
    
    token = create_access_token({ 
        "id" : str(tryuser.id) 
        })
    return token
@db_session
def get_account_user(id : uuid.UUID):
    user = UserModel[id]
    if(user == None):
        raise Exception("not found user")
    
    chats : list = [read_link_chat(c.id) for c in user.chats]

    return  {"login": user.login, 
             "nickname" : user.nickName, 
             "group": user.group, 
             "chats" : chats} 
