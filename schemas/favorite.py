from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    """
    收藏状态响应模型类
    """
    is_favorite: bool = Field(...,alias = "isFavorite")


class FavoriteRequest(BaseModel):
    """
    收藏请求模型类
    """
    news_id: int = Field(...,alias = "newsId")


#两个类：新闻模型类 + 收藏类
class FavoriteNewsItemBase(NewsItemBase):
    favorite_id : int = Field(...,alias = "favoriteId")
    favorite_time : datetime = Field(alias = "favoriteTime")

    model_config = ConfigDict(
        populate_by_name = True,
        from_attributes=True,
    )

#收藏列表的相应接口模型类
class FavoriteListResponse(BaseModel):
    """
    收藏列表响应模型类
    """
    list: list[FavoriteNewsItemBase]
    total: int
    has_more:bool = Field(alias = "hasMore")

    model_config = ConfigDict(
        populate_by_name = True,
        from_attributes=True,
    )

