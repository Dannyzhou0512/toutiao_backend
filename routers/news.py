from fastapi import FastAPI, APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.util import total_size

from config.db_conf import get_db
from crud import news_cache

#创建APIRouter实例
#prefix路由前缀（API接口规范文档）
#tags 分组标签
routers =  APIRouter(prefix = "/api/news",tags = ["news"])


#接口的实现流程
#1. 模块化路由→API接口文档
#2. 定义模型类→数据库列表（数据库设计文档）
#3. 在crud文件夹当中创建文件，封装操作数据库的方法
#4. 在路由处理函数当中调用cRud封装好的方法等待相应的结果


@routers.get("/categories")
async def get_categories(skip:int = 0, limit:int = 100,db:AsyncSession = Depends(get_db)):
    #先获取数据库里面新闻分类数据→先定义模型类→ 封装查询数据的方法
    categories = await news_cache.get_categories(db,skip,limit)
    return {
        "code" : 200,
        "message": "获取分类成功",
        "data": categories
    }

@routers.get("/list")
async def get_news_list(
        category_id:int = Query(...,alias = "categoryId"),   #alias是表示起别名
        page:int = 1,
        page_size:int = Query(...,alias = "pageSize",le = 100),   #前端在接入这个接口的时候必须要加入参数
        db:AsyncSession = Depends(get_db)   #依赖注入机制
):
    #思路：处理分页的规则→查询新闻的列表→计算总量→计算是否还有更多
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db,category_id,offset,page_size)
    total = await news_cache.get_news_count(db,category_id)
    #hasMore = total > offset + page_size
    hasMore = total > offset + page_size
    return {
        "code" : 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": hasMore
        }
    }

@routers.get("/detail")
async def get_news_detail(news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news_cache.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    views_res = await news_cache.increase_news_views(db, news_id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    related_news = await news_cache.get_related_news(db, news_id, news_detail.category_id)

    return {
      "code": 200,
      "message": "success",
      "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
      }
    }
