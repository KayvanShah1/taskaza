from app.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_task(db: AsyncSession, user_id: int, task_data: dict) -> Task:
    task = Task(**task_data, user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Task).where(Task.user_id == user_id))
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    return result.scalar_one_or_none()


async def update_task(db: AsyncSession, task: Task, updated_data: dict):
    for key, value in updated_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(db: AsyncSession, task: Task, new_status: str):
    task.status = new_status
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()
