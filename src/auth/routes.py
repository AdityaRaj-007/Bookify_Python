from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from .schemas import CreateUserModel, UserModel, UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import create_access_token,decode_access_token,verify_password
from datetime import datetime, timedelta
from .dependencies import RefreshTokenBearer,AccessTokenBearer
from src.db.redis import add_token_to_blocklist

auth_router = APIRouter()

user_service = UserService()

REFRESH_TOKEN_EXPIRY = 2

@auth_router.post('/signup',status_code=status.HTTP_201_CREATED,response_model=UserModel)
async def create_user_account(user_data:CreateUserModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exits(email,session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already exists, please log in!")
    
    user = await user_service.create_user(user_data,session)

    return user

@auth_router.post('/login')
async def login(user_data: UserLoginModel,session:AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password
    print(f"User email {email}")
    print(f"User password {password}")

    user = await user_service.get_user_by_email(email,session)

    print(f"User: {user}")

    if user is not None:
        password_valid = verify_password(password,user.password_hash)
        print(f"Is password valid? {password_valid}")

        if password_valid:
            access_token = create_access_token(user_data={'email':user.email,'user_uid':str(user.uid)})

            refresh_token = create_access_token(
                user_data={'email':user.email,'user_uid':str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(content={
                "message":"Login successful!",
                "access_token":access_token,
                "refresh_token":refresh_token,
                "user":{
                    "email": user.email,
                    "uid":str(user.uid)
                }
            })
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid email or password!")


@auth_router.get('/refresh_token')
async def get_new_access_token(token_data:dict = Depends(RefreshTokenBearer())):
    expiry_time = token_data['exp']
    
    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_access_token(user_data=token_data['user'])

        return JSONResponse(content={
            "access_token": new_access_token
        })


    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or exprired token!")

@auth_router.get('/logout')
async def logout(token_data:dict = Depends(AccessTokenBearer())):

    jti = token_data['jti']

    await add_token_to_blocklist(jti)

    return JSONResponse(content={"message":"Logged out successfully!"},status_code=status.HTTP_200_OK)
