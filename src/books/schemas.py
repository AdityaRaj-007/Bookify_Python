from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import date,datetime


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author:str
    publisher:str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

class CreateBookModel(BaseModel):
    title: str
    author:str
    publisher:str
    published_date: str
    page_count: int
    language: str