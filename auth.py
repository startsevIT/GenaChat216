import uuid
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

SECRET = "secret_secret_secret_secret_secret_secret_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

def get_token(request: Request):
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

def validate_token(token : str) -> uuid:
    try:
        payload = jwt.decode(token[7:], SECRET, algorithms=ALGORITHM)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')
    
    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')
    
    user_id = payload.get('id')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')
    return user_id
    
def get_user_id(request : Request) -> uuid:
    return validate_token(get_token(request))