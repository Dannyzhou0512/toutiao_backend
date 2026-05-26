from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News
from models.users import User

from schemas.base import NewsItemBase


#检查收藏的状态：当前用户是否 收藏了这条新闻
async def is_news_favorite(db: AsyncSession,
                           user: User,
                           news_id: int,):

    query = select(Favorite).where(Favorite.user_id == user.id, Favorite.news_id == news_id)
    result = await db.execute(query)
    #是否有收藏的记录
    return result.scalar_one_or_none() is not None


async def add_news_favorite(db: AsyncSession,
                           user_id: int,
                           news_id: int,):
    # 创建收藏记录
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

#取消收藏
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int,
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0   #命中的布尔值


#获取收藏列表：获取的是某个用户的收藏列表 + 分页功能
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
):
    #总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    #获取收藏列表 -- 联表查询 join() + 收藏时间排序 + 分页
    #select(查询主体模型类，字段名).join(联合查询的模型类，联合查询的条件).where().order_by().offset().limit()
    #别名：Favorite.created_at.label(favorite_time")
    offset = (page - 1) * page_size
    query = (select(News, Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))  #这里为什么要起别名，因为在表进行联立的时候两个表里面有相同的字段，所以起别名防止后期命名冲突
     .join(Favorite, Favorite.news_id == News.id)
     .where(Favorite.user_id == user_id)
     .order_by(Favorite.created_at.desc())
     .offset(offset).limit(page_size))

    list_result = await db.execute(query)
    rows = list_result.all()

    # 3. 关键：必须返回 rows 和 total
    return rows, total


#情况收藏列表：当前用户的收藏列表
async def clear_favorite_list(
        db: AsyncSession,
        user_id: int,
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0   #rowcount指的是命中的数量