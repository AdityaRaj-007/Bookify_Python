from .models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .schemas import CreateUserModel
from .utils import generate_hashed_password

class UserService:

    async def get_user_by_email(self,email:str, session:AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        user = result.first()

        return user 

    async def user_exits(self,email:str, session:AsyncSession):
        user = await self.get_user_by_email(email,session)

        if user is None:
            return False
        
        return True
    
    async def create_user(self,user_data: CreateUserModel, session: AsyncSession):
        data = user_data.model_dump()

        hashed_password = generate_hashed_password(data["password"])

        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password_hash=hashed_password,
            role="user"
        )

        session.add(user)

        await session.commit()

        return user

        