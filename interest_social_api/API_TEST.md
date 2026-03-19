# 兴趣社交APP API 单元测试文档

## 测试环境配置

### 安装依赖
```bash
pip install -r requirements.txt
```

### 初始化数据库
```bash
python init_db.py
```

### 启动服务
```bash
python run.py
```

服务地址: `http://127.0.0.1:5000`

---

## 一、用户认证模块测试

### 1.1 用户注册

**接口**: `POST /api/auth/register`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "123456",
    "nickname": "新用户",
    "bio": "这是我的简介",
    "gender": 1,
    "location": "北京"
  }'
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-50字符 |
| password | string | 是 | 密码，至少6字符 |
| nickname | string | 否 | 昵称，默认为用户名 |
| avatar | string | 否 | 头像URL |
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
      "id": 5,
      "username": "newuser",
      "nickname": "新用户",
      "avatar": "",
      "bio": "这是我的简介",
      "gender": 1,
      "birthday": "",
      "location": "北京",
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

**失败响应 - 用户名已存在** (400):
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

**失败响应 - 参数错误** (400):
```json
{
  "code": 400,
  "message": "用户名长度必须在3-50个字符之间",
  "data": null
}
```

---

### 1.2 用户登录

**接口**: `POST /api/auth/login`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user1",
    "password": "123456"
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
      "id": 1,
      "username": "test_user1",
      "nickname": "测试用户1",
      "avatar": "https://picsum.photos/200/200?random=1",
      "bio": "这是测试用户1的简介",
      "gender": 1,
      "birthday": "",
      "location": "北京",
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:00:00Z",
      "followers_count": 0,
      "following_count": 0,
      "posts_count": 0,
      "likes_count": 0
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

**失败响应 - 凭证错误** (401):
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

---

### 1.3 Token验证

**接口**: `GET /api/auth/verify`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**请求头**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| Authorization | string | 是 | Bearer Token |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "令牌有效",
  "data": {
    "user": {
      "id": 1,
      "username": "test_user1",
      "nickname": "测试用户1",
      "avatar": "https://picsum.photos/200/200?random=1",
      "bio": "这是测试用户1的简介",
      "gender": 1,
      "birthday": "",
      "location": "北京",
      "is_verified": false,
      "verified_type": "",
      "created_at": "2024-03-19T10:00:00Z"
    },
    "is_valid": true
  }
}
```

**失败响应 - 无效Token** (401):
```json
{
  "code": 401,
  "message": "令牌无效或已过期",
  "data": null
}
```

---

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

---

### 1.5 修改密码

**接口**: `POST /api/auth/change-password`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/auth/change-password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "123456",
    "new_password": "654321"
  }'
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码，至少6字符 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

---

## 二、帖子功能模块测试

### 2.1 获取帖子列表

**接口**: `GET /api/posts`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/posts?page=1&page_size=10&topic=摄影"
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
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
        "username": "测试用户1",
        "user_avatar": "https://picsum.photos/200/200?random=1",
        "content": "今天天气真好！",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 10,
        "comments_count": 5,
        "shares_count": 2,
        "created_at": "2024-03-19T10:30:00Z",
        "is_deleted": false
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "has_more": false
  }
}
```

---

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
    "post": {
      "id": 1,
      "user_id": 1,
      "username": "测试用户1",
      "user_avatar": "https://picsum.photos/200/200?random=1",
      "content": "今天天气真好，出去拍照啦！",
      "images": ["https://example.com/image1.jpg"],
      "topic": "#摄影技巧#",
      "likes_count": 0,
      "comments_count": 0,
      "shares_count": 0,
      "created_at": "2024-03-19T10:30:00Z",
      "is_deleted": false
    }
  }
}
```

---

### 2.3 获取帖子详情

**接口**: `GET /api/posts/<post_id>`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/posts/1
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "username": "测试用户1",
    "user_avatar": "https://picsum.photos/200/200?random=1",
    "content": "今天天气真好，出去拍照啦！",
    "images": [],
    "topic": "#摄影技巧#",
    "likes_count": 10,
    "comments_count": 5,
    "shares_count": 2,
    "created_at": "2024-03-19T10:30:00Z",
    "is_deleted": false,
    "comments": [
      {
        "id": 1,
        "post_id": 1,
        "user_id": 2,
        "username": "测试用户2",
        "user_avatar": "https://picsum.photos/200/200?random=2",
        "content": "拍得真好看！",
        "parent_id": null,
        "created_at": "2024-03-19T11:00:00Z"
      }
    ]
  }
}
```

---

### 2.4 删除帖子

**接口**: `DELETE /api/posts/<post_id>`

**请求示例**:
```bash
curl -X DELETE http://127.0.0.1:5000/api/posts/1 \
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

**失败响应 - 无权限** (403):
```json
{
  "code": 403,
  "message": "无权删除此帖子",
  "data": null
}
```

---

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
    "likes_count": 11
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
    "likes_count": 10
  }
}
```

---

### 2.6 获取评论列表

**接口**: `GET /api/posts/<post_id>/comments`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/posts/1/comments?page=1&page_size=20"
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
        "username": "测试用户2",
        "user_avatar": "https://picsum.photos/200/200?random=2",
        "content": "拍得真好看！",
        "parent_id": null,
        "created_at": "2024-03-19T11:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false
  }
}
```

---

### 2.7 发表评论

**接口**: `POST /api/posts/<post_id>/comments`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/posts/1/comments \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这条帖子写得真好！",
    "parent_id": null
  }'
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 评论内容，最多1000字符 |
| parent_id | int | 否 | 父评论ID(回复评论时) |

**成功响应** (201):
```json
{
  "code": 200,
  "message": "评论成功",
  "data": {
    "comment": {
      "id": 1,
      "post_id": 1,
      "user_id": 1,
      "username": "测试用户1",
      "user_avatar": "https://picsum.photos/200/200?random=1",
      "content": "这条帖子写得真好！",
      "parent_id": null,
      "created_at": "2024-03-19T12:00:00Z"
    }
  }
}
```

---

### 2.8 图片上传

**接口**: `POST /api/upload/image`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/upload/image \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "image=@/path/to/image.jpg"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "image": {
      "id": 1,
      "filename": "a1b2c3d4e5f6.jpg",
      "url": "/uploads/1/a1b2c3d4e5f6.jpg",
      "size": 102400,
      "created_at": "2024-03-19T12:00:00Z"
    }
  }
}
```

**失败响应 - 格式不支持** (400):
```json
{
  "code": 400,
  "message": "不支持的文件格式",
  "data": null
}
```

---

## 三、社交互动模块测试

### 3.1 关注用户

**接口**: `POST /api/social/follow/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/follow/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "关注成功",
  "data": {
    "is_following": true,
    "followers_count": 1,
    "following_count": 1
  }
}
```

**失败响应 - 已关注** (400):
```json
{
  "code": 400,
  "message": "已经关注了该用户",
  "data": null
}
```

---

### 3.2 取消关注

**接口**: `POST /api/social/unfollow/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/unfollow/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "取消关注成功",
  "data": {
    "is_following": false,
    "followers_count": 0,
    "following_count": 0
  }
}
```

---

### 3.3 获取关注列表

**接口**: `GET /api/social/following`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/following?page=1&page_size=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "following": [
      {
        "id": 2,
        "username": "test_user2",
        "nickname": "测试用户2",
        "avatar": "https://picsum.photos/200/200?random=2",
        "bio": "这是测试用户2的简介",
        "gender": 2,
        "birthday": "",
        "location": "上海",
        "is_verified": false,
        "verified_type": "",
        "created_at": "2024-03-19T10:00:00Z",
        "followed_at": "2024-03-19T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false
  }
}
```

---

### 3.4 获取粉丝列表

**接口**: `GET /api/social/followers`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/followers?page=1&page_size=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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
        "username": "test_user2",
        "nickname": "测试用户2",
        "avatar": "https://picsum.photos/200/200?random=2",
        "bio": "这是测试用户2的简介",
        "gender": 2,
        "birthday": "",
        "location": "上海",
        "is_verified": false,
        "verified_type": "",
        "created_at": "2024-03-19T10:00:00Z",
        "followed_at": "2024-03-19T12:00:00Z",
        "is_following": false
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false
  }
}
```

---

### 3.5 拉黑用户

**接口**: `POST /api/social/blacklist/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/blacklist/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "拉黑成功",
  "data": {
    "is_blocked": true
  }
}
```

---

### 3.6 取消拉黑

**接口**: `POST /api/social/unblacklist/<user_id>`

**请求示例**:
```bash
curl -X POST http://127.0.0.1:5000/api/social/unblacklist/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "取消拉黑成功",
  "data": {
    "is_blocked": false
  }
}
```

---

### 3.7 获取黑名单列表

**接口**: `GET /api/social/blacklist`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/social/blacklist?page=1&page_size=20" \
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
        "id": 2,
        "username": "test_user2",
        "nickname": "测试用户2",
        "avatar": "https://picsum.photos/200/200?random=2",
        "bio": "这是测试用户2的简介",
        "gender": 2,
        "birthday": "",
        "location": "上海",
        "is_verified": false,
        "verified_type": "",
        "created_at": "2024-03-19T10:00:00Z",
        "blocked_at": "2024-03-19T12:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false
  }
}
```

---

### 3.8 检查关注状态

**接口**: `GET /api/social/check-follow/<user_id>`

**请求示例**:
```bash
curl -X GET http://127.0.0.1:5000/api/social/check-follow/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "is_following": true,
    "is_blocked": false,
    "is_blocked_by": false
  }
}
```

---

## 四、搜索发现模块测试

### 4.1 搜索用户

**接口**: `GET /api/search/users`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/users?keyword=测试&page=1&page_size=20"
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "username": "test_user1",
        "nickname": "测试用户1",
        "avatar": "https://picsum.photos/200/200?random=1",
        "bio": "这是测试用户1的简介",
        "gender": 1,
        "birthday": "",
        "location": "北京",
        "is_verified": false,
        "verified_type": "",
        "created_at": "2024-03-19T10:00:00Z",
        "followers_count": 10
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false,
    "keyword": "测试"
  }
}
```

---

### 4.2 搜索帖子

**接口**: `GET /api/search/posts`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/posts?keyword=摄影&topic=摄影技巧&page=1&page_size=20"
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| topic | string | 否 | 话题筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

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
        "username": "测试用户1",
        "user_avatar": "https://picsum.photos/200/200?random=1",
        "content": "今天天气真好，出去拍照啦！",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 10,
        "comments_count": 5,
        "shares_count": 2,
        "created_at": "2024-03-19T10:30:00Z",
        "is_deleted": false
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false,
    "keyword": "摄影",
    "topic": "摄影技巧"
  }
}
```

---

### 4.3 搜索话题

**接口**: `GET /api/search/topics`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/topics?keyword=摄影&page=1&page_size=20"
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
        "description": "分享摄影技巧和心得",
        "posts_count": 12580,
        "created_at": "2024-03-19T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "has_more": false,
    "keyword": "摄影"
  }
}
```

---

### 4.4 综合搜索

**接口**: `GET /api/search/all`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/all?keyword=摄影"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "users": [
      {
        "id": 3,
        "username": "photographer",
        "nickname": "摄影大师",
        "avatar": "https://picsum.photos/200/200?random=3",
        "bio": "用镜头记录美好生活",
        "gender": 1,
        "birthday": "",
        "location": "深圳",
        "is_verified": true,
        "verified_type": "兴趣达人",
        "created_at": "2024-03-19T10:00:00Z",
        "followers_count": 5
      }
    ],
    "posts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "测试用户1",
        "user_avatar": "https://picsum.photos/200/200?random=1",
        "content": "摄影技巧分享",
        "images": [],
        "topic": "#摄影技巧#",
        "likes_count": 10,
        "comments_count": 5,
        "shares_count": 2,
        "created_at": "2024-03-19T10:30:00Z",
        "is_deleted": false
      }
    ],
    "topics": [
      {
        "id": 1,
        "name": "#摄影技巧#",
        "description": "分享摄影技巧和心得",
        "posts_count": 12580,
        "created_at": "2024-03-19T10:00:00Z"
      }
    ],
    "keyword": "摄影"
  }
}
```

---

### 4.5 获取热门话题

**接口**: `GET /api/search/hot-topics`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/hot-topics?limit=10"
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
        "description": "分享摄影技巧和心得",
        "posts_count": 12580,
        "created_at": "2024-03-19T10:00:00Z"
      },
      {
        "id": 2,
        "name": "#旅行日记#",
        "description": "记录旅行中的美好瞬间",
        "posts_count": 9870,
        "created_at": "2024-03-19T10:00:00Z"
      }
    ]
  }
}
```

---

### 4.6 搜索建议

**接口**: `GET /api/search/suggest`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5000/api/search/suggest?keyword=摄&limit=10"
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggestions": [
      {
        "type": "user",
        "id": 3,
        "name": "摄影大师",
        "avatar": "https://picsum.photos/200/200?random=3",
        "subtitle": "@photographer"
      },
      {
        "type": "topic",
        "id": 1,
        "name": "#摄影技巧#",
        "subtitle": "12580 帖子"
      }
    ]
  }
}
```

---

## 五、测试脚本

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
            "password": "123456",
            "nickname": "API测试用户"
        }
        response = requests.post(url, json=data)
        print(f"注册响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    
    def test_login(self):
        """测试登录"""
        url = f"{BASE_URL}/api/auth/login"
        data = {
            "username": "test_user1",
            "password": "123456"
        }
        response = requests.post(url, json=data)
        result = response.json()
        print(f"登录响应: {response.status_code}")
        if result['code'] == 200:
            self.token = result['data']['token']
            self.user_id = result['data']['user']['id']
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    
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
        return response.json()
    
    def test_get_posts(self):
        """测试获取帖子列表"""
        url = f"{BASE_URL}/api/posts"
        response = requests.get(url)
        print(f"获取帖子列表响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    
    def test_follow(self, user_id):
        """测试关注"""
        url = f"{BASE_URL}/api/social/follow/{user_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(url, headers=headers)
        print(f"关注响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    
    def test_search(self, keyword):
        """测试搜索"""
        url = f"{BASE_URL}/api/search/all?keyword={keyword}"
        response = requests.get(url)
        print(f"搜索响应: {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 50)
        print("开始API测试")
        print("=" * 50)
        
        print("\n1. 测试登录...")
        self.test_login()
        
        print("\n2. 测试发布帖子...")
        self.test_create_post()
        
        print("\n3. 测试获取帖子列表...")
        self.test_get_posts()
        
        print("\n4. 测试关注用户...")
        self.test_follow(2)
        
        print("\n5. 测试搜索...")
        self.test_search("摄影")
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)

if __name__ == "__main__":
    tester = TestAPI()
    tester.run_all_tests()
```

---

## 六、错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 禁止访问/无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 七、注意事项

1. 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer <token>`
2. Token有效期为24小时，过期后需要重新登录
3. 图片上传支持的格式：png, jpg, jpeg, gif
4. 图片大小限制：16MB
5. 帖子内容最多5000字符
6. 评论内容最多1000字符
