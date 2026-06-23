from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models import User, UserRole
from app.repositories.user import user_repository
from app.schemas.crud import UserCreate

class UserService:
    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User | None:
        user = await user_repository.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def register(self, db: AsyncSession, user_data: UserCreate) -> User:
        try:
            role = UserRole(user_data.role)
        except ValueError:
            role = UserRole.VIEWER

        user_in = {
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "role": role,
            "is_active": True,
        }
        user = await user_repository.create(db, obj_in=user_in)
        return user

user_service = UserService()
