"""User repository — data access layer for the User model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Data access for the User model.

    create() accepts raw credentials (post-hashing) rather than a Pydantic
    schema because the plain-text password must never leave the service layer.
    """

    model = User

    async def create(self, *, email: str, hashed_password: str) -> User:
        """
        Persist a new user with pre-hashed credentials.

        The caller (UserService) is responsible for hashing the password
        before passing it here. This method never sees plain-text passwords.
        """
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Lookup a user by email address. Used by auth workflows."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
