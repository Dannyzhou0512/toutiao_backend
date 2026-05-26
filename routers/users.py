from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import false, true
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import users
from crud.users import get_username
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserupdateRequest, UserChangePasswordRequest
from config.db_conf import get_db
from utils import security
from utils.auth import get_current_user
from utils.response import success_response

routers = APIRouter(prefix="/api/user", tags=["users"])

@routers.post("/register")
async def register(userdata:UserRequest,db:AsyncSession = Depends(get_db)):  #用户信息和db
    # 注册流程： 验证用户是否存在 → 创建用户 → 生成Token → 响应结果
    existing_user = await users.get_username(db,userdata.username)
    if existing_user:
        raise HTTPException(status_code=400,detail="用户已存在")
    user = await users.create_user(db,userdata)
    token = await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data":{
    #     "token":token,
    #     "userInfo":{
    #     "id":user.id,
    #     "username":user.username,
    #     "bio":user.bio,
    #     "avatar":user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token = token,user_info = UserInfoResponse.model_validate(user))
    return success_response(message = "注册成功",data = response_data)

@routers.post("/login")
async def login(userdata:UserRequest,db:AsyncSession = Depends(get_db)):
    # 登录流程： 验证用户是否存在 → 验证密码是否正确 → 生成Token → 响应结果
    user = await users.authenticate(db,userdata.username,userdata.password)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")

    token = await users.create_token(db,user.id)

    response_data = UserAuthResponse(token = token,user_info = UserInfoResponse.model_validate(user))
    return success_response(message = "登录成功",data = response_data)

#查询Token查用户 →封装crud→功能整合成一个工具函数和→路由导入使用：依赖注入
@routers.get("/info")
async def get_user_info(user:User = Depends(get_current_user)):
    return success_response(message = "获取用户信息成功",data = UserInfoResponse.model_validate(user))


#修改用户信息：验证Token→更新（用户输入数据 put 提交 → 请求体参数 → 定义pydantic模型类）→ 响应结果
#参数：用户输入的+验证的Token + db(调用更新的方法)
@routers.put("/update")
async def update_user_info(userdata:UserupdateRequest,user:User = Depends(get_current_user),
                           db:AsyncSession = Depends(get_db)):

    updated_user  = await users.update_user(db,user.username,userdata)
    return success_response(message = "修改用户信息成功",data = UserInfoResponse.model_validate(updated_user))



#修改密码：验证Token→更新（用户输入数据 put 提交 → 请求体参数 → 验证密码是否正确 → 密码加密 → 密码更新）→ 响应结果
@routers.put("/password")
async def update_password(password_data:UserChangePasswordRequest,
                          user:User = Depends(get_current_user),
                          db:AsyncSession = Depends(get_db)):
    """
    修改密码流程：
    1. 验证旧密码是否正确
    2. 新密码加密
    3. 修改密码
    """
    res_change_pwd = await users.update_password(password_data.old_password,password_data.new_password,user,db)
    if not res_change_pwd:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="旧密码错误")
    return success_response(message = "修改密码成功")
