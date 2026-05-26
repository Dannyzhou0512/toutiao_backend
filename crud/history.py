from datetime import datetime


from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News
from models.users import User

#添加历史记录
async def add_history(db: AsyncSession,
                      user_id: int,
                      news_id: int,
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:   #如果历史记录当中存在则进行及时更新的操作
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:   #如果不存在则进行添加操作
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


#获取浏览历史的相关记录
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
):
    offset = (page - 1) * page_size

    count_query = (
        select(func.count(History.id))
        .where(History.user_id == user_id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = (
        select(
            News,
            History.view_time.label("view_time"),
            History.id.label("history_id")
        )
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()

    return rows, total

#删除历史记录
async def delete_history(
        news_id: int,
        db: AsyncSession,
        user_id: int,
):
    stmt = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 清空当前用户的浏览历史
async def clear_history(
        db: AsyncSession,
        user_id: int,
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
