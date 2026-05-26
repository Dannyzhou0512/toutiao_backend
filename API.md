# API 文档

基础地址：`http://127.0.0.1:8000`

除注册、登录和新闻查询外，收藏与浏览历史接口均需要 `Authorization` 请求头。

## 用户

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/user/register` | 注册用户并返回 token |
| `POST` | `/api/user/login` | 登录并返回 token |
| `GET` | `/api/user/info` | 获取当前用户信息 |
| `PUT` | `/api/user/update` | 更新个人信息 |
| `PUT` | `/api/user/password` | 修改密码 |

注册和登录请求体：

```json
{
  "username": "demo",
  "password": "123456"
}
```

修改密码请求体：

```json
{
  "oldPassword": "123456",
  "newPassword": "new_password"
}
```

## 新闻

| 方法 | 路径 | 参数 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/api/news/categories` | `skip`, `limit` | 获取分类 |
| `GET` | `/api/news/list` | `categoryId`, `page`, `pageSize` | 获取分页新闻列表 |
| `GET` | `/api/news/detail` | `id` | 获取详情、增加浏览量并返回相关新闻 |

示例：

```http
GET /api/news/list?categoryId=1&page=1&pageSize=10
```

## 收藏

| 方法 | 路径 | 参数/请求体 | 说明 |
| --- | --- | --- | --- |
| `GET` | `/api/favorite/check` | `newsId` | 查询收藏状态 |
| `POST` | `/api/favorite/add` | `{ "newsId": 1 }` | 新增收藏 |
| `DELETE` | `/api/favorite/remove?newsId=1` | `newsId` | 取消收藏 |
| `GET` | `/api/favorite/list` | `page`, `pageSize` | 获取收藏列表 |
| `DELETE` | `/api/favorite/clear` | 无 | 清空收藏 |

## 浏览历史

| 方法 | 路径 | 参数/请求体 | 说明 |
| --- | --- | --- | --- |
| `POST` | `/api/history/add` | `{ "newsId": 1 }` | 新增或刷新浏览记录 |
| `GET` | `/api/history/list` | `page`, `pageSize` | 获取浏览历史 |
| `DELETE` | `/api/history/delete/{news_id}` | 新闻 ID | 删除当前用户对该新闻的浏览记录 |
| `DELETE` | `/api/history/clear` | 无 | 清空当前用户浏览历史 |

删除接口使用新闻 ID，是为了与前端新闻卡片的 `item.id` 保持一致：

```http
DELETE /api/history/delete/1
Authorization: <token>
```

## 状态码

| 状态码 | 说明 |
| --- | --- |
| `200` | 操作成功 |
| `400` | 数据冲突或请求无法处理 |
| `401` | token 无效或过期 |
| `404` | 资源不存在 |
| `422` | 参数格式错误或缺少必填参数 |
| `500` | 服务端或数据库异常 |
