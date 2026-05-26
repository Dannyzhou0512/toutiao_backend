# Toutiao News Backend

基于 FastAPI、SQLAlchemy Async、MySQL 和 Redis 的新闻资讯后端服务，提供用户认证、新闻浏览、收藏和浏览历史接口。

## 功能

- 用户注册、登录、资料更新和密码修改
- 新闻分类、列表、详情与相关新闻
- 收藏状态、收藏列表、取消收藏与清空收藏
- 浏览记录新增、查询、单条删除与清空
- Redis 新闻数据缓存
- 统一 JSON 响应和异常处理


## 项目运行效果

以下页面为本地前端运行效果示例，访问地址示例：`http://localhost:5173/home`。

### 首页新闻列表

首页支持新闻分类切换、新闻列表展示、新闻来源与阅读量展示，并在右侧显示新闻缩略图。

![首页新闻列表](01-home-news.png)

### 全部分类

分类页集中展示新闻分类入口，用户可以快速进入头条、社会、国内、国际、娱乐、体育、科技和财经等频道。

![全部分类](02-category-list.png)

### AI 问答

AI 问答页提供基础对话交互，用户可以输入问题并查看助手回复。

![AI问答](03-ai-chat.png)

### 我的收藏

收藏页展示用户已收藏的新闻内容，支持查看收藏时间，并可对单条收藏进行删除。

![我的收藏](04-favorites.png)

### 浏览历史

浏览历史页记录用户访问过的新闻，支持查看浏览时间，并可删除单条记录或清空历史。

![浏览历史](05-history.png)

## 技术栈

| 组件 | 用途 |
| --- | --- |
| FastAPI | HTTP API 框架 |
| SQLAlchemy Async + aiomysql | MySQL 异步访问 |
| Redis | 新闻缓存 |
| Pydantic | 请求和响应模型 |
| Passlib + bcrypt | 密码散列 |
| Uvicorn | ASGI 服务器 |

## 项目结构

```text
toutiao_backend/
├── cache/        # Redis 缓存键和操作
├── config/       # 数据库与 Redis 配置
├── crud/         # 数据访问和业务操作
├── models/       # SQLAlchemy ORM 模型
├── routers/      # FastAPI 路由
├── schemas/      # Pydantic 模型
├── sql/          # 数据库初始化脚本
├── utils/        # 鉴权、密码和响应处理
├── API.md        # 接口说明
├── main.py       # 应用入口
└── requirements.txt
```

## 快速开始

### 1. 创建虚拟环境并安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 初始化 MySQL

创建表结构：

```powershell
cmd /c "mysql -u root -p < sql\schema.sql"
```

项目不会上传数据库密码。启动前通过环境变量设置本地连接地址：

```powershell
$env:DATABASE_URL = "mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4"
```

`sql/schema.sql` 只创建表结构。请自行导入或创建新闻分类与新闻数据。

### 3. 启动 Redis

Redis 用于新闻缓存；Redis 不可用时缓存读写会跳过，但 MySQL 仍必须可用。

如 Redis 不在默认地址，可设置：

```powershell
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "0"
```

### 4. 启动 API

```powershell
python -m uvicorn main:app --reload
```

服务地址：`http://127.0.0.1:8000`  
交互文档：`http://127.0.0.1:8000/docs`

## 配置

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | `mysql+aiomysql://root:@localhost:3306/news_app?charset=utf8mb4` | MySQL 异步连接串 |
| `SQL_ECHO` | `false` | 是否输出 SQL 日志 |
| `REDIS_HOST` | `localhost` | Redis 主机 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_DB` | `0` | Redis 数据库编号 |
| `DEBUG_MODE` | `false` | 是否向 API 响应输出错误详情 |

可参考 [.env.example](.env.example)，但应用读取的是系统环境变量。

## 响应结构

成功响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

鉴权接口需要请求头：

```http
Authorization: <login-response-token>
```

后端同时兼容 `Bearer <token>` 格式。

## 接口文档

接口列表和参数说明见 [API.md](API.md)。

## 安全说明

- 不要提交实际 `DATABASE_URL`、用户 token 或生产环境配置。
- `DEBUG_MODE=true` 会在错误响应中返回调试信息，仅适合本地开发。
- `.venv`、IDE 配置和本地环境文件均已加入 `.gitignore`。
