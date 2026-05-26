
from datetime import datetime, timedelta
import uuid
from email.policy import default
from fastapi import HTTPException

from fastapi import Depends
from sqlalchemy import select, update, false
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.users import User, UserToken
from schemas.users import UserRequest, UserupdateRequest
from utils import security
from utils.auth import get_current_user


#根据用户名查询数据库
async def get_username(db:AsyncSession,username:str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db:AsyncSession,user_data:UserRequest):
    #先做一下密码的加密处理→add
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  #从数据库当中读取回新的 User
    return user



#生成Token
async def create_token(db: AsyncSession, user_id: int):
    #生成Token + 设置过期的时间 + 查询数据库当前用户是否有Token → 有：更新 ，没有：添加
    token = str(uuid.uuid4())
    #这里设置七天为截至日期
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

async def authenticate(db:AsyncSession,username:str,password:str):
    user = await get_username(db,username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None

    return user

#根据Token用户查询：验证Token，查询用户
async def get_user_by_token(db:AsyncSession,token:str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#用户更新:update更新 → 检查是否命中 → 获取更新后来用户返回
async def update_user(db:AsyncSession,username:str,user_date:UserupdateRequest):
#用户更新前先进行字段的查询
#model_dump→这是 Pydantic 的方法，意思是把这个对象转换成一个普通的 Python 字典（dict）。
#** 的作用是把一个字典“拆散”成一个个独立的键值对参数：  一开始拆成了字典之后就是通过**讲对应的字典的数值拆成了对应的键值对
    query = update(User).where(User.username == username).values(**user_date.model_dump(
        exclude_unset=True, #exclude_unset=True：非常关键！ 意思是“排除掉那些前端根本没传的字段”。
        exclude_none=True   #exclude_none=True：意思是“排除掉值为 None 的字段”。
    ))
    result = await db.execute(query)
    await db.commit()

#检查更新操作
    if result.rowcount == 0:
        raise HTTPException(status_code=404,detail="用户不存在")

#获取一下更新之后的用户
    update_user = await get_username(db,username)
    return update_user

# #修改密码：验证旧密码 → 新密码加密 → 修改密码
# async def update_password(old_password:str,new_password:str,user:User,
#                         db:AsyncSession = Depends(get_db)):
#     """
#     修改密码流程：
#     1. 验证旧密码是否正确
#     2. 新密码加密
#     3. 修改密码
#     """
#     if not security.verify_password(old_password,user.password):
#         return  False
#
#     hashed_password = security.get_hash_password(new_password)
#     user.password = hashed_password
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return True


#修改密码：验证旧密码 → 新密码加密 → 修改密码
async def update_password(old_password:str,new_password:str,user:User,
                        db:AsyncSession):
    """
    修改密码流程：
    1. 验证旧密码是否正确
    2. 新密码加密
    3. 修改密码
    """
    if not security.verify_password(old_password,user.password):
        return  False

    hashed_password = security.get_hash_password(new_password)
    user.password = hashed_password
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True