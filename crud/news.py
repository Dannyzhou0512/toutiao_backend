from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy import update

from models.news import Category, News


async def get_categories(db:AsyncSession,skip:int = 0,limit:int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_new_list(
        db:AsyncSession,
        category_id:int,
        skip:int = 0,
        limit:int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db:AsyncSession,category_id:int):
    #查询的是指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()   #只能有一个结果否则会报错


async def get_news_detail(db:AsyncSession,news_id:int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession,news_id:int):
   stmt = update(News).where(News.id == news_id).values(views=News.views+1)
   result = await db.execute(stmt)
   await db.commit()
   #更新→检查数据库是否真的命中了数据，命中率返回True
   return result.rowcount > 0

async def get_related_news(db:AsyncSession,category_id:int,news_id:int):
    stmt = select(News).where(News.category_id == category_id, News.id != news_id).order_by(
       News.views.desc()   #默认为升序，此时desc为降序
    ).limit(5)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]

