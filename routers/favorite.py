from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteRequest, FavoriteListResponse, FavoriteNewsItemBase
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite, news

routers = APIRouter(
    prefix="/api/favorite",
    tags=["收藏"],
)

@routers.get("/check")
async def check_favorite(news_id: int = Query(..., alias="newsId"),
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)
):
    is_favorite = await favorite.is_news_favorite(db, user, news_id)
    return success_response(message = "查询收藏状态成功",data=FavoriteCheckResponse(isFavorite = is_favorite))


@routers.post("/add")
async def add_favorite(
        data:FavoriteRequest,   #pydantic类型
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message = "收藏成功",data =  result)

#取消收藏
@routers.delete("/remove")
async def delete_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.remove_news_favorite(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
    return success_response(message = "取消收藏成功")

@routers.get("/list")
async def get_favorite_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
        user: User = Depends(get_current_user),      #这边是认证Token的已经封装好了
        db: AsyncSession = Depends(get_db)
):
    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,    #意思是将每一行拆解开
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in rows]
    has_more = total > page * page_size

    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)

#清空收藏列表
@routers.delete("/clear")
async def clear_favorite_list(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count = await favorite.clear_favorite_list(db, user.id)
    return success_response(message=f"清空了{count}条数据")