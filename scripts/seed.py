"""
Seed script – create initial admin + sample employees.
Run: python -m scripts.seed
"""
import asyncio
from datetime import datetime
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User, UserRole


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Admin
        admin = User(
            phone="972501111111",
            full_name="גיא – מנהל",
            role=UserRole.ADMIN,
            is_active=True,
            is_onboarding_complete=True,
            hired_at=datetime.utcnow(),
        )
        db.add(admin)

        # Sample employees
        employees = [
            ("972502222222", "יוסי כהן"),
            ("972503333333", "מיכל לוי"),
            ("972504444444", "איתי מזרחי"),
        ]
        for phone, name in employees:
            db.add(User(
                phone=phone,
                full_name=name,
                role=UserRole.EMPLOYEE,
                is_active=True,
                hired_at=datetime.utcnow(),
            ))

        await db.commit()
        print("Seed completed – admin + 3 employees created")


if __name__ == "__main__":
    asyncio.run(seed())
