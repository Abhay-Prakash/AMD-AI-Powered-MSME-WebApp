import asyncio
from app.db.session import engine
from app.models.registration import PendingRegistration

async def create_table():
    async with engine.begin() as conn:
        print("Creating pending_registrations table...")
        await conn.run_sync(PendingRegistration.metadata.create_all)
        print("Done.")

if __name__ == "__main__":
    asyncio.run(create_table())
