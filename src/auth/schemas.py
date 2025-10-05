from datetime import datetime
from typing import List
import uuid
from pydantic import BaseModel, Field, EmailStr
from src.books.schemas import Book

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

class UserBooksModel(UserModel):
    books: List[Book]

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)