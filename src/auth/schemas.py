from datetime import datetime
import uuid
from pydantic import BaseModel, Field, EmailStr

class CreateUserModel(BaseModel):
    username:str = Field(max_length=8)
    email: EmailStr 
    first_name:str
    last_name:str
    password: str = Field(min_length=8)

class UserModel(BaseModel):
    uid: uuid.UUID
    username:str
    email:str
    first_name:str
    last_name:str
    is_verified:bool
    password_hash: str = Field(exclude=True)
    created_at: datetime 
    updated_at: datetime

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)