from typing import Any, List
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .utils import decode_access_token
from src.db.redis import token_in_blocklist
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .service import UserService
from .models import User

user_service = UserService()

class TokenBearer(HTTPBearer):
    
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)


    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds =  await super().__call__(request)

        token = creds.credentials

        token_data = decode_access_token(token)

        if not self.validate_token(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={
                "error":"This token is invalid or has been revoked",
                "resolution":"Please log in again!!"
            })
        
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail={
                "error":"This token is invalid or has been revoked",
                "resolution":"Please log in again!!"
            })
        
        self.verify_token_data(token_data)

        return token_data
    
    def validate_token(self,token:str) -> bool:

        token_data = decode_access_token(token)

        if token_data is not None:
            return True
        
        return False
    
    def verify_token_data(self,token_data):
        raise NotImplementedError("Please override this method in child classes.")
    
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please provide an access token")

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Please provide a refresh token")
        
async def get_current_user(token_data: dict = Depends(AccessTokenBearer()),session:AsyncSession = Depends(get_session)):
    user_email = token_data['user']['email']

    user = await user_service.get_user_by_email(user_email,session)

    return user


class RoleChecker:
    def __init__(self,allowed_roles:List[str]) -> None:

        self.allowed_roles = allowed_roles

    def __call__(self, current_user:User = Depends(get_current_user)) -> Any:
        if current_user.role in self.allowed_roles:
            return True
        
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Operation not permitted!")