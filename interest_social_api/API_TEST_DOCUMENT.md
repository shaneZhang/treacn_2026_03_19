# API 单元测试文档

## 测试环境配置

- **服务地址**: `http://127.0.0.1:5000`
- **数据格式**: JSON
- **认证方式**: Bearer Token (JWT)

## 通用响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

---

## 一、用户认证模块

### 1.1 用户注册

**接口**: `POST /api/auth/register`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456",
    "nickname": "测试用户",
    "bio": "这是一个测试用户",
    "gender": 1,
    "location": "北京市"
  }'
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-20个字符 |
| password | string | 是 | 密码，至少6个字符 |
| nickname | string | 否 | 昵称，默认为用户名 |
| bio | string | 否 | 个人简介 |
| gender | int | 否 | 性别(0未知/1男/2女) |
| birthday | string | 否 | 生日 |
| location | string | 否 | 位置 |

**成功响应** (201):
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 2,
      "username": "testuser",
      "nickname": "测试用户",
      "avatar": "https://picsum.photos/200/200?random=2",
      "bio": "这是一个测试用户",
      "gender": 1,
      "birthday": "",
      "location": "北京市",
      "followers_count": 0,
      "following_count": 0,
      "posts_count": 0,
      "likes_count": 0,
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

### 1.2 用户登录

**接口**: `POST /api/auth/login`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test123456"
  }'
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": 2,
      "username": "testuser",
      "nickname": "测试用户",
      "avatar": "https://picsum.photos/200/200?random=2",
      "bio": "这是一个测试用户",
      "gender": 1,
      "birthday": "",
      "location": "北京市",
      "followers_count": 0,
      "following_count": 0,
      "posts_count": 0,
      "likes_count": 0,
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**错误响应** (401):
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

### 1.3 Token验证

**接口**: `GET /api/auth/verify`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "令牌有效",
  "data": {
    "user": {
      "id": 2,
      "username": "testuser",
      "nickname": "测试用户",
      "avatar": "https://picsum.photos/200/200?random=2",
      "bio": "这是一个测试用户",
      "gender": 1,
      "birthday": "",
      "location": "北京市",
      "followers_count": 0,
      "following_count": 0,
      "posts_count": 0,
      "likes_count": 0,
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:30:00Z"
    },
    "is_valid": true
  }
}
```

**错误响应** (401):
```json
{
  "code": 401,
  "message": "令牌已过期",
  "data": null
}
```

### 1.4 用户登出

**接口**: `POST /api/auth/logout`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 1.5 修改密码

**接口**: `PUT /api/auth/password`

**请求示例**:
```bash
curl -X PUT http://127.0.0.1:5000/api/auth/password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "test123456",
    "new_password": "newpassword123"
  }'
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码，至少6个字符 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

## 二、帖子功能模块

### 2.1 获取帖子列表

**接口**: `GET /api/posts`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/posts?page=1&per_page=10&topic=#摄影技巧#"
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |
| topic | string | 否 | 话题筛选 |
| user_id | int | 否 | 用户ID筛选 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "posts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "管理员",
        "user_avatar": "",
        "content": "今天天气真好！",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 5,
        "comments_count": 2,
        "shares_count": 0,
        "created_at": "2024-03-19T10:30:00Z",
        "is_liked": false
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false
  }
}
```

### 2.2 发布帖子

**接口**: `POST /api/posts`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/posts \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天天气真好，出去拍照啦！",
    "images": ["https://example.com/image1.jpg"],
    "topic": "#摄影技巧#"
  }'
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 帖子内容，最多5000字符 |
| images | array | 否 | 图片URL数组 |
| topic | string | 否 | 话题 |

**成功响应** (201):
```json
{
  "code": 200,
  "message": "发布成功",
  "data": {
    "id": 2,
    "user_id": 2,
    "username": "测试用户",
    "user_avatar": "https://picsum.photos/200/200?random=2",
    "content": "今天天气真好，出去拍照啦！",
    "images": ["https://example.com/image1.jpg"],
    "topic": "#摄影技巧#",
    "likes_count": 0,
    "comments_count": 0,
    "shares_count": 0,
    "created_at": "2024-03-19T11:00:00Z",
    "is_liked": false
  }
}
```

### 2.3 获取帖子详情

**接口**: `GET /api/posts/<post_id>`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/posts/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "username": "管理员",
    "user_avatar": "",
    "content": "今天天气真好！",
    "images": [],
    "topic": "#摄影技巧#",
    "likes_count": 5,
    "comments_count": 2,
    "shares_count": 0,
    "created_at": "2024-03-19T10:30:00Z",
    "is_liked": false
  }
}
```

**错误响应** (404):
```json
{
  "code": 404,
  "message": "帖子不存在",
  "data": null
}
```

### 2.4 删除帖子

**接口**: `DELETE /api/posts/<post_id>`

**请求示例**:
```bash
curl -X DELETE http://127.0.0.1:5000/api/posts/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**错误响应** (403):
```json
{
  "code": 403,
  "message": "无权删除此帖子",
  "data": null
}
```

### 2.5 点赞/取消点赞

**接口**: `POST /api/posts/<post_id>/like`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/posts/1/like \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**点赞成功响应** (200):
```json
{
  "code": 200,
  "message": "点赞成功",
  "data": {
    "is_liked": true,
    "likes_count": 6
  }
}
```

**取消点赞成功响应** (200):
```json
{
  "code": 200,
  "message": "取消点赞成功",
  "data": {
    "is_liked": false,
    "likes_count": 5
  }
}
```

### 2.6 获取评论列表

**接口**: `GET /api/posts/<post_id>/comments`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/posts/1/comments?page=1&per_page=10"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "comments": [
      {
        "id": 1,
        "post_id": 1,
        "user_id": 2,
        "nickname": "测试用户",
        "avatar": "https://picsum.photos/200/200?random=2",
        "content": "拍得真好看！",
        "reply_to": null,
        "created_at": "2024-03-19T11:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false
  }
}
```

### 2.7 发表评论

**接口**: `POST /api/posts/<post_id>/comments`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/posts/1/comments \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "拍得真好看！",
    "reply_to_id": null
  }'
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 评论内容，最多500字符 |
| reply_to_id | int | 否 | 回复的评论ID |

**成功响应** (201):
```json
{
  "code": 200,
  "message": "评论成功",
  "data": {
    "id": 2,
    "post_id": 1,
    "user_id": 2,
    "nickname": "测试用户",
    "avatar": "https://picsum.photos/200/200?random=2",
    "content": "拍得真好看！",
    "reply_to": null,
    "created_at": "2024-03-19T12:00:00Z"
  }
}
```

### 2.8 图片上传

**接口**: `POST /api/upload`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/upload \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@/path/to/image.jpg"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "/uploads/a1b2c3d4e5f6.jpg",
    "filename": "a1b2c3d4e5f6.jpg"
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "不支持的文件类型",
  "data": null
}
```

---

## 三、社交互动模块

### 3.1 关注用户

**接口**: `POST /api/social/follow/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/follow/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "关注成功",
  "data": {
    "is_following": true,
    "followers_count": 1
  }
}
```

**错误响应** (400):
```json
{
  "code": 400,
  "message": "已经关注了该用户",
  "data": null
}
```

### 3.2 取消关注

**接口**: `POST /api/social/unfollow/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/unfollow/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "取消关注成功",
  "data": {
    "is_following": false,
    "followers_count": 0
  }
}
```

### 3.3 获取关注列表

**接口**: `GET /api/social/following/<user_id>`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/following/2?page=1&per_page=10"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "following": [
      {
        "id": 1,
        "nickname": "管理员",
        "avatar": "https://picsum.photos/200/200?random=1",
        "bio": "系统管理员",
        "is_following": true,
        "followed_at": "2024-03-19T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false
  }
}
```

### 3.4 获取粉丝列表

**接口**: `GET /api/social/followers/<user_id>`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/followers/1?page=1&per_page=10"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "followers": [
      {
        "id": 2,
        "nickname": "测试用户",
        "avatar": "https://picsum.photos/200/200?random=2",
        "bio": "这是一个测试用户",
        "is_following": false,
        "followed_at": "2024-03-19T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false
  }
}
```

### 3.5 获取黑名单

**接口**: `GET /api/social/blacklist`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/blacklist?page=1&per_page=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "blacklist": [
      {
        "id": 3,
        "nickname": "不良用户",
        "avatar": "https://picsum.photos/200/200?random=3",
        "bio": "",
        "blocked_at": "2024-03-19T13:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false
  }
}
```

### 3.6 添加黑名单

**接口**: `POST /api/social/blacklist/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/blacklist/3 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "已加入黑名单",
  "data": {
    "is_blocked": true
  }
}
```

### 3.7 移除黑名单

**接口**: `DELETE /api/social/blacklist/<user_id>`

**请求示例**:
```bash
curl -X DELETE http://127.0.0.1:5000/api/social/blacklist/3 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "已移出黑名单",
  "data": {
    "is_blocked": false
  }
}
```

### 3.8 检查关注状态

**接口**: `GET /api/social/check-follow/<user_id>`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/social/check-follow/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_following": true,
    "is_followed": false,
    "is_blocked": false
  }
}
```

---

## 四、搜索发现模块

### 4.1 搜索用户

**接口**: `GET /api/search/users`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/users?keyword=测试&page=1&per_page=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "users": [
      {
        "id": 2,
        "nickname": "测试用户",
        "avatar": "https://picsum.photos/200/200?random=2",
        "bio": "这是一个测试用户",
        "followers_count": 0,
        "is_following": false
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false,
    "keyword": "测试"
  }
}
```

### 4.2 搜索帖子

**接口**: `GET /api/search/posts`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/posts?keyword=天气&topic=#摄影技巧#&page=1&per_page=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| topic | string | 否 | 话题筛选 |
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "posts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "管理员",
        "user_avatar": "",
        "content": "今天天气真好！",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 5,
        "comments_count": 2,
        "shares_count": 0,
        "created_at": "2024-03-19T10:30:00Z",
        "is_liked": false
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false,
    "keyword": "天气",
    "topic": "#摄影技巧#"
  }
}
```

### 4.3 搜索话题

**接口**: `GET /api/search/topics`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/topics?keyword=摄影&page=1&per_page=10"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "topics": [
      {
        "id": 1,
        "name": "#摄影技巧#",
        "posts_count": 12580,
        "trend": "up"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 10,
    "has_more": false,
    "keyword": "摄影"
  }
}
```

### 4.4 获取热门话题

**接口**: `GET /api/search/hot-topics`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/hot-topics?limit=5"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "topics": [
      {
        "id": 1,
        "name": "#摄影技巧#",
        "posts_count": 12580,
        "trend": "up"
      },
      {
        "id": 2,
        "name": "#旅行日记#",
        "posts_count": 9870,
        "trend": "up"
      },
      {
        "id": 3,
        "name": "#美食分享#",
        "posts_count": 8650,
        "trend": "stable"
      }
    ]
  }
}
```

### 4.5 全局搜索

**接口**: `GET /api/search`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search?keyword=摄影" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "keyword": "摄影",
    "users": [],
    "posts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "管理员",
        "user_avatar": "",
        "content": "今天天气真好！",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 5,
        "comments_count": 2,
        "shares_count": 0,
        "created_at": "2024-03-19T10:30:00Z",
        "is_liked": false
      }
    ],
    "topics": [
      {
        "id": 1,
        "name": "#摄影技巧#",
        "posts_count": 12580,
        "trend": "up"
      }
    ]
  }
}
```

---

## 五、错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 六、测试脚本

### Python测试脚本示例

```python
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

class TestAPI:
    def __init__(self):
        self.token = None
        self.user_id = None
    
    def test_register(self):
        """测试注册"""
        url = f"{BASE_URL}/api/auth/register"
        data = {
            "username": "testuser_api",
            "password": "test123456",
            "nickname": "API测试用户"
        }
        response = requests.post(url, json=data)
        print(f"注册响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        if response.status_code == 201:
            self.token = response.json()['data']['token']
            self.user_id = response.json()['data']['user']['id']
        return response
    
    def test_login(self):
        """测试登录"""
        url = f"{BASE_URL}/api/auth/login"
        data = {
            "username": "testuser_api",
            "password": "test123456"
        }
        response = requests.post(url, json=data)
        print(f"登录响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        if response.status_code == 200:
            self.token = response.json()['data']['token']
        return response
    
    def test_create_post(self):
        """测试发布帖子"""
        url = f"{BASE_URL}/api/posts"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "content": "这是一条测试帖子",
            "topic": "#测试话题#"
        }
        response = requests.post(url, json=data, headers=headers)
        print(f"发布帖子响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response
    
    def test_get_posts(self):
        """测试获取帖子列表"""
        url = f"{BASE_URL}/api/posts"
        response = requests.get(url)
        print(f"获取帖子列表响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response
    
    def test_search(self):
        """测试搜索"""
        url = f"{BASE_URL}/api/search"
        params = {"keyword": "测试"}
        response = requests.get(url, params=params)
        print(f"搜索响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response

if __name__ == "__main__":
    api = TestAPI()
    api.test_register()
    api.test_create_post()
    api.test_get_posts()
    api.test_search()
```

### 运行测试

```bash
# 启动服务
cd /Users/zhangyuqing/Desktop/trae_2026_03_19/interest_social_api
PYTHONPATH=/tmp/pylibs:$PYTHONPATH python run.py

# 在另一个终端运行测试
python test_api.py
```
