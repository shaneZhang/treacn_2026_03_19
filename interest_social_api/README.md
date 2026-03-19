# 兴趣社交APP API 接口文档

## 基础信息

- **服务地址**: `http://127.0.0.1:5000`
- **数据格式**: JSON
- **编码格式**: UTF-8

## 通用响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200表示成功 |
| message | string | 提示信息 |
| data | object | 响应数据 |

---

## 接口列表

### 1. 首页数据接口

**请求路径**: `GET /api/home`

**接口说明**: 获取APP首页的推荐内容，包括轮播图、热门话题、推荐用户、推荐帖子等

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| banners | array | 轮播图列表 |
| hot_topics | array | 热门话题列表 |
| recommended_users | array | 推荐用户列表 |
| recommended_posts | array | 推荐帖子列表 |
| interest_categories | array | 兴趣分类列表 |

**banners 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 轮播图ID |
| title | string | 标题 |
| image | string | 图片URL |
| link | string | 跳转链接 |
| link_type | string | 链接类型(event/h5/activity) |

**hot_topics 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 话题ID |
| name | string | 话题名称 |
| posts_count | int | 帖子数量 |
| trend | string | 趋势(up/down/stable) |

---

### 2. 我的（用户中心）

**请求路径**: `GET /api/profile`

**接口说明**: 获取当前登录用户的基本信息和统计数据

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user | object | 用户基本信息 |
| stats | object | 用户统计数据 |

**user 对象结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| username | string | 用户名 |
| nickname | string | 昵称 |
| avatar | string | 头像URL |
| bio | string | 个人简介 |
| gender | int | 性别(0未知/1男/2女) |
| birthday | string | 生日 |
| location | string | 位置 |
| followers_count | int | 粉丝数 |
| following_count | int | 关注数 |
| posts_count | int | 帖子数 |
| likes_count | int | 获赞数 |
| is_verified | bool | 是否认证 |
| verified_type | string | 认证类型 |
| created_at | string | 注册时间 |

---

### 3. 我的帖子

**请求路径**: `GET /api/profile/posts`

**接口说明**: 获取当前用户发布的所有帖子

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| posts | array | 帖子列表 |
| total | int | 总数 |
| page | int | 当前页码 |
| page_size | int | 每页数量 |

---

### 4. 粉丝列表

**请求路径**: `GET /api/profile/followers`

**接口说明**: 获取当前用户的粉丝列表

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| followers | array | 粉丝列表 |
| total | int | 总数 |
| has_more | bool | 是否还有更多 |

---

### 5. 关注列表

**请求路径**: `GET /api/profile/following`

**接口说明**: 获取当前用户关注的用户列表

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| following | array | 关注列表 |
| total | int | 总数 |
| has_more | bool | 是否还有更多 |

---

### 6. 点赞列表

**请求路径**: `GET /api/profile/liked`

**接口说明**: 获取当前用户点赞过的帖子列表

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| posts | array | 帖子列表 |
| total | int | 总数 |
| page | int | 当前页码 |
| page_size | int | 每页数量 |

---

### 7. 通知列表

**请求路径**: `GET /api/messages/notifications`

**接口说明**: 获取当前用户收到的所有通知，包括点赞、评论、关注、系统通知等

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| notifications | array | 通知列表 |
| unread_count | int | 未读数量 |
| total | int | 总数 |

**notifications 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 通知ID |
| type | string | 通知类型(like/comment/follow/system) |
| user_id | int | 触发用户ID |
| user_nickname | string | 触发用户昵称 |
| user_avatar | string | 触发用户头像 |
| content | string | 通知内容 |
| post_id | int | 相关帖子ID |
| is_read | bool | 是否已读 |
| created_at | string | 创建时间 |

---

### 8. 会话列表

**请求路径**: `GET /api/messages/conversations`

**接口说明**: 获取当前用户的所有私信会话列表

**请求参数**: 无

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| conversations | array | 会话列表 |
| total | int | 总数 |
| total_unread | int | 总未读数 |

**conversations 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| conversation_id | int | 会话ID |
| user_id | int | 对方用户ID |
| nickname | string | 对方昵称 |
| avatar | string | 对方头像 |
| last_message | string | 最后一条消息 |
| last_message_time | string | 最后消息时间 |
| unread_count | int | 未读数量 |
| is_online | bool | 是否在线 |

---

### 9. 私信详情

**请求路径**: `GET /api/messages/private/<user_id>`

**接口说明**: 获取与指定用户的私信聊天记录

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 对方用户ID |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| messages | array | 消息列表 |
| total | int | 消息总数 |

**messages 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 消息ID |
| from_user_id | int | 发送者ID |
| from_user_nickname | string | 发送者昵称 |
| from_user_avatar | string | 发送者头像 |
| to_user_id | int | 接收者ID |
| content | string | 消息内容 |
| is_read | bool | 是否已读 |
| created_at | string | 发送时间 |

---

### 10. 发送私信

**请求路径**: `POST /api/messages/send`

**接口说明**: 向指定用户发送私信

**请求头**: `Content-Type: application/json`

**请求体**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| to_user_id | int | 是 | 接收者用户ID |
| content | string | 是 | 消息内容 |

**请求示例**:

```json
{
  "to_user_id": 2001,
  "content": "你好！很高兴认识你"
}
```

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| message | object | 发送成功的消息对象 |

---

### 11. 检查已读状态

**请求路径**: `GET /api/messages/check-read/<user_id>`

**接口说明**: 检查指定用户发送给当前用户的消息是否已读

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 对方用户ID |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | int | 用户ID |
| has_unread | bool | 是否有未读消息 |
| unread_count | int | 未读消息数量 |

---

### 12. 新闻列表

**请求路径**: `GET /api/news`

**接口说明**: 获取新闻列表，支持分页

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认10 |
| type | string | 否 | 新闻类型，默认all |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| news | array | 新闻列表 |
| total | int | 总数 |
| page | int | 当前页码 |
| page_size | int | 每页数量 |
| has_more | bool | 是否还有更多 |

**news 数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 新闻ID |
| title | string | 标题 |
| summary | string | 摘要 |
| image | string | 图片URL |
| source | string | 来源 |
| publish_time | string | 发布时间 |
| views_count | int | 阅读量 |
| comments_count | int | 评论数 |
| is_hot | bool | 是否热门 |

---

### 13. 新闻详情

**请求路径**: `GET /api/news/<news_id>`

**接口说明**: 获取单条新闻的详细内容

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| news_id | int | 是 | 新闻ID |

**响应数据**: 返回单条新闻对象，结构同上

---

### 14. 检查更新

**请求路径**: `GET /api/system/check-update`

**接口说明**: 检查APP是否有新版本可用

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | string | 否 | 当前版本号 |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| has_update | bool | 是否有更新 |
| latest_version | string | 最新版本号 |
| min_supported_version | string | 最低支持版本 |
| update_content | string | 更新内容 |
| download_url | string | 下载链接 |
| force_update | bool | 是否强制更新 |
| release_date | string | 发布日期 |

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 启动项目

```bash
cd interest_social_api
pip install -r requirements.txt
python run.py
```

服务启动后访问 `http://127.0.0.1:5000` 查看所有接口列表。
