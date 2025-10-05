from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from src.books.schemas import Book, BookUpdateModel,CreateBookModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import BookService
from src.auth.dependencies import AccessTokenBearer
from src.auth.dependencies import RoleChecker

book_router = APIRouter()
book_service = BookService()
authorization = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin","user"]))

@book_router.get('/',response_model=List[Book],dependencies=[role_checker])
async def get_all_books(session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)):

    print(token_details)
    books = await book_service.get_all_books(session)
    if not books:
        return JSONResponse(content={"message":"No books found!"},status_code=404)
    return books

@book_router.get('/user/{user_uid}',response_model=List[Book],dependencies=[role_checker])
async def get_user_books(user_uid:str,session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)):

    print(token_details)
    books = await book_service.get_all_user_books(user_uid,session)
    if not books:
        return JSONResponse(content={"message":"No books found!"},status_code=404)
    return books

@book_router.post('/addBook',status_code=status.HTTP_201_CREATED,response_model=Book,dependencies=[role_checker])
async def add_book(book_data:CreateBookModel, session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)) -> dict:
    user_id = token_details.get('user')['user_uid']
    new_book = await book_service.add_book(book_data,user_id,session)
    return new_book

@book_router.get('/{book_uid}',response_model=Book,dependencies=[role_checker])
async def get_single_book(book_uid:str, session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)) -> dict:
    book = await book_service.get_book(book_uid,session)

    if book: 
        return book
    else:        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")

@book_router.patch('/updateBook/{book_uid}',response_model=Book,dependencies=[role_checker])
async def update_book_data(book_uid:str,book_update_data:BookUpdateModel, session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)) -> dict:
    
    updated_book = await book_service.update_book(book_uid,book_update_data,session)

    if updated_book:
        return updated_book
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")

@book_router.delete('/deleteBook/{book_uid}',dependencies=[role_checker])
async def delete_book(book_uid:str, session:AsyncSession = Depends(get_session),token_details:dict=Depends(authorization)) -> dict:
    deleted = await book_service.delete_book(book_uid,session)
    
    if deleted:
        return {"message": f"Book with id {book_uid} deleted successfully!"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found!")