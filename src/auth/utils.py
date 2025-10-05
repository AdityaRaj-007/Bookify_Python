import jwt
import uuid
import logging
from datetime import datetime, timedelta
from passlib.context import CryptContext
from src.config import Config


password_context = CryptContext(
    schemes=['bcrypt']
)

TOKEN_EXPIRY_TIME = 3600

def generate_hashed_password(password:str) -> str:
    hashed_password = password_context.hash(password)

    return hashed_password

def verify_password(password:str,hash:str) -> bool:
    return password_context.verify(password, hash)

def create_access_token(user_data:dict, expiry:timedelta = None, refresh:bool = False):
    payload = {}

    payload['user'] = user_data
    payload['exp'] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=TOKEN_EXPIRY_TIME))
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGO
    )

    return token

def decode_access_token(token:str) -> dict:
    try:
        token_data = jwt.decode(jwt=token,key=Config.JWT_SECRET_KEY,algorithms=[Config.JWT_ALGO])

        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None