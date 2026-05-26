from fastapi import FastAPI  # 1. 引入 FastAPI 类
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware

from routers.users import register
from utils.exception_handler import register_exception_handler

app = FastAPI()             # 2. 实例化一个 app 对象，名字必须叫 app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 明确指定前端地址    #允许的源，开发阶段允许所有的源，生产环境需要指定的源
    allow_credentials=True, #允许携带cookie
    allow_methods=["*"],    #允许的请求方法
    allow_headers=["*"],    #允许的请求头
)
#注册异常处理器
register_exception_handler(app)


#挂载路由/注册路由
app.include_router(news.routers)
app.include_router(users.routers)
app.include_router(favorite.routers)
app.include_router(history.routers)

