from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from src.books.schemas import Book, BookUpdateModel,CreateBookModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import BookService
from src.auth.dependencies import AccessTokenBearer

book_router = APIRouter()
book_service = BookService()
authorization = AccessTokenBearer()


@book_router.get('/',response_model=List[Book])
async def get_all_books(session:AsyncSession = Depends(get_session),user_details=Depends(authorization)):

    print(user_details)
    books = await book_service.get_all_books(session)
    if not books:
        return JSONResponse(content={"message":"No books found!"},status_code=404)
    return books

@book_router.post('/addBook',status_code=status.HTTP_201_CREATED,response_model=Book)
async def add_book(book_data:CreateBookModel, session:AsyncSession = Depends(get_session),user_details=Depends(authorization)) -> dict:
    new_book = await book_service.add_book(book_data,session)
    return new_book

@book_router.get('/{book_uid}',response_model=Book)
async def get_single_book(book_uid:str, session:AsyncSession = Depends(get_session),user_details=Depends(authorization)) -> dict:
    book = await book_service.get_book(book_uid,session)

    if book: 
        return book
    else:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")

@book_router.patch('/updateBook/{book_uid}',response_model=Book)
async def update_book_data(book_uid:str,book_update_data:BookUpdateModel, session:AsyncSession = Depends(get_session),user_details=Depends(authorization)) -> dict:
    
    updated_book = await book_service.update_book(book_uid,book_update_data,session)

    if updated_book:
        return updated_book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")

@book_router.delete('/deleteBook/{book_uid}')
async def delete_book(book_uid:str, session:AsyncSession = Depends(get_session),user_details=Depends(authorization)) -> dict:
    deleted = await book_service.delete_book(book_uid,session)
    
    if deleted:
        return {"message": f"Book with id {book_uid} deleted successfully!"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")