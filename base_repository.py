"""Generic async base repository providing standard CRUD primitives."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing get, list, save, and delete.

    Concrete repositories must declare a `model` class attribute and
    implement their own `create` and `update` methods with appropriate
    schema types. Those operations are intentionally excluded here because
    their argument types differ per domain model.

    Usage:
        class UserRepository(BaseRepository[User]):
            model = User

            async def create(self, *, email: str, hashed_password: str) -> User:
                ...
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, record_id: UUID) -> ModelT | None:
        """Fetch a single record by primary key. Returns None if not found."""
        stmt = select(self.model).where(  # type: ignore[attr-defined]
            self.model.id == record_id  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> list[ModelT]:
        """Fetch a paginated list ordered by creation date descending."""
        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, instance: ModelT) -> ModelT:
        """
        Commit in-place attribute changes on a tracked instance and refresh it.

        Use this pattern after setting attributes directly on a fetched record:
            user.is_active = False
            await repo.save(user)
        """
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """
        Hard-delete a record from the database.

        Do NOT use this on models that carry SoftDeleteMixin — those should
        be deactivated via a status field or deleted_at timestamp instead.
        """
        await self.session.delete(instance)
        await self.session.commit()
