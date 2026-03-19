# 兴趣社交APP API 接口文档

## 项目简介

这是一个基于Flask框架开发的兴趣类社交App后端API服务，采用SQLite数据库进行数据持久化存储，支持用户认证、帖子发布、社交互动、搜索发现等功能。

## 技术栈

- **框架**: Flask 3.0.0
- **数据库**: SQLite + Flask-SQLAlchemy
- **认证**: JWT (PyJWT)
- **密码加密**: Werkzeug security
- **跨域支持**: Flask-Cors

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
python run.py
```

服务将在 `http://127.0.0.1:5000` 启动

## 基础信息

- **服务地址**: `http://127.0.0.1:5000`
- **数据格式**: JSON
- **编码格式**: UTF-8
- **认证方式**: Bearer Token (JWT)

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

### 一、用户认证模块

#### 1.1 用户注册

**请求路径**: `POST /api/auth/register`

**接口说明**: 注册新用户账号

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

**请求示例**:
```json
{
  "username": "testuser",
  "password": "test123456",
  "nickname": "测试用户",
  "bio": "这是一个测试用户",
  "gender": 1,
  "location": "北京市"
}
```

**响应数据**:
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

#### 1.2 用户登录

**请求路径**: `POST /api/auth/login`

**接口说明**: 用户登录获取Token

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```json
{
  "username": "testuser",
  "password": "test123456"
}
```

**响应数据**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": { ... },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### 1.3 Token验证

**请求路径**: `GET /api/auth/verify`

**接口说明**: 验证Token是否有效

**请求头**: `Authorization: Bearer <token>`

**响应数据**:
```json
{
  "code": 200,
  "message": "令牌有效",
  "data": {
    "user": { ... },
    "is_valid": true
  }
}
```

#### 1.4 用户登出

**请求路径**: `POST /api/auth/logout`

**接口说明**: 用户登出，使Token失效

**请求头**: `Authorization: Bearer <token>`

**响应数据**:
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

#### 1.5 修改密码

**请求路径**: `PUT /api/auth/password`

**接口说明**: 修改用户密码

**请求头**: `Authorization: Bearer <token>`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码，至少6个字符 |

**请求示例**:
```json
{
  "old_password": "test123456",
  "new_password": "newpassword123"
}
```

---

### 二、帖子功能模块

#### 2.1 获取帖子列表

**请求路径**: `GET /api/posts`

**接口说明**: 获取帖子列表，支持分页和筛选

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |
| topic | string | 否 | 话题筛选 |
| user_id | int | 否 | 用户ID筛选 |

**响应数据**:
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
    "per_page": 20,
    "has_more": false
  }
}
```

#### 2.2 发布帖子

**请求路径**: `POST /api/posts`

**接口说明**: 发布新帖子

**请求头**: `Authorization: Bearer <token>`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 帖子内容，最多5000字符 |
| images | array | 否 | 图片URL数组 |
| topic | string | 否 | 话题 |

**请求示例**:
```json
{
  "content": "今天天气真好，出去拍照啦！",
  "images": ["https://example.com/image1.jpg"],
  "topic": "#摄影技巧#"
}
```

#### 2.3 获取帖子详情

**请求路径**: `GET /api/posts/<post_id>`

**接口说明**: 获取指定帖子的详细信息

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| post_id | int | 是 | 帖子ID |

#### 2.4 删除帖子

**请求路径**: `DELETE /api/posts/<post_id>`

**接口说明**: 删除指定帖子（仅作者可删除）

**请求头**: `Authorization: Bearer <token>`

#### 2.5 点赞/取消点赞

**请求路径**: `POST /api/posts/<post_id>/like`

**接口说明**: 对帖子进行点赞或取消点赞

**请求头**: `Authorization: Bearer <token>`

**响应数据**:
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

#### 2.6 获取评论列表

**请求路径**: `GET /api/posts/<post_id>/comments`

**接口说明**: 获取帖子的评论列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

#### 2.7 发表评论

**请求路径**: `POST /api/posts/<post_id>/comments`

**接口说明**: 对帖子发表评论

**请求头**: `Authorization: Bearer <token>`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 评论内容，最多500字符 |
| reply_to_id | int | 否 | 回复的评论ID |

**请求示例**:
```json
{
  "content": "拍得真好看！",
  "reply_to_id": null
}
```

#### 2.8 图片上传

**请求路径**: `POST /api/upload`

**接口说明**: 上传图片文件

**请求头**: 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 图片文件，支持png/jpg/jpeg/gif |

**响应数据**:
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

---

### 三、社交互动模块

#### 3.1 关注用户

**请求路径**: `POST /api/social/follow/<user_id>`

**接口说明**: 关注指定用户

**请求头**: `Authorization: Bearer <token>`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 要关注的用户ID |

**响应数据**:
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

#### 3.2 取消关注

**请求路径**: `POST /api/social/unfollow/<user_id>`

**接口说明**: 取消关注指定用户

**请求头**: `Authorization: Bearer <token>`

#### 3.3 获取关注列表

**请求路径**: `GET /api/social/following/<user_id>`

**接口说明**: 获取指定用户的关注列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

#### 3.4 获取粉丝列表

**请求路径**: `GET /api/social/followers/<user_id>`

**接口说明**: 获取指定用户的粉丝列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

#### 3.5 获取黑名单

**请求路径**: `GET /api/social/blacklist`

**接口说明**: 获取当前用户的黑名单列表

**请求头**: `Authorization: Bearer <token>`

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

#### 3.6 添加黑名单

**请求路径**: `POST /api/social/blacklist/<user_id>`

**接口说明**: 将指定用户加入黑名单

**请求头**: `Authorization: Bearer <token>`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 要拉黑的用户ID |

#### 3.7 移除黑名单

**请求路径**: `DELETE /api/social/blacklist/<user_id>`

**接口说明**: 将指定用户移出黑名单

**请求头**: `Authorization: Bearer <token>`

#### 3.8 检查关注状态

**请求路径**: `GET /api/social/check-follow/<user_id>`

**接口说明**: 检查与指定用户的关注关系

**请求头**: `Authorization: Bearer <token>`

**响应数据**:
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

### 四、搜索发现模块

#### 4.1 搜索用户

**请求路径**: `GET /api/search/users`

**接口说明**: 根据关键词搜索用户

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

**响应数据**:
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
    "per_page": 20,
    "has_more": false,
    "keyword": "测试"
  }
}
```

#### 4.2 搜索帖子

**请求路径**: `GET /api/search/posts`

**接口说明**: 根据关键词或话题搜索帖子

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| topic | string | 否 | 话题筛选 |
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

#### 4.3 搜索话题

**请求路径**: `GET /api/search/topics`

**接口说明**: 根据关键词搜索话题

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| page | int | 否 | 页码，默认1 |
| per_page | int | 否 | 每页数量，默认20 |

**响应数据**:
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
    "per_page": 20,
    "has_more": false,
    "keyword": "摄影"
  }
}
```

#### 4.4 获取热门话题

**请求路径**: `GET /api/search/hot-topics`

**接口说明**: 获取热门话题列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回数量，默认10 |

#### 4.5 全局搜索

**请求路径**: `GET /api/search`

**接口说明**: 全局搜索用户、帖子、话题

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |

**响应数据**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "keyword": "摄影",
    "users": [...],
    "posts": [...],
    "topics": [...]
  }
}
```

---

### 五、原有接口（保留）

#### 5.1 首页数据

**请求路径**: `GET /api/home`

**接口说明**: 获取APP首页的推荐内容

#### 5.2 我的（用户中心）

**请求路径**: `GET /api/profile`

**接口说明**: 获取当前登录用户的基本信息

#### 5.3 我的帖子

**请求路径**: `GET /api/profile/posts`

**接口说明**: 获取当前用户发布的所有帖子

#### 5.4 粉丝列表

**请求路径**: `GET /api/profile/followers`

**接口说明**: 获取当前用户的粉丝列表

#### 5.5 关注列表

**请求路径**: `GET /api/profile/following`

**接口说明**: 获取当前用户关注的用户列表

#### 5.6 点赞列表

**请求路径**: `GET /api/profile/liked`

**接口说明**: 获取当前用户点赞过的帖子列表

#### 5.7 通知列表

**请求路径**: `GET /api/messages/notifications`

**接口说明**: 获取当前用户收到的所有通知

#### 5.8 会话列表

**请求路径**: `GET /api/messages/conversations`

**接口说明**: 获取当前用户的所有私信会话列表

#### 5.9 私信详情

**请求路径**: `GET /api/messages/private/<user_id>`

**接口说明**: 获取与指定用户的私信聊天记录

#### 5.10 发送私信

**请求路径**: `POST /api/messages/send`

**接口说明**: 向指定用户发送私信

#### 5.11 新闻列表

**请求路径**: `GET /api/news`

**接口说明**: 获取新闻列表

#### 5.12 新闻详情

**请求路径**: `GET /api/news/<news_id>`

**接口说明**: 获取指定新闻的详细信息

#### 5.13 检查更新

**请求路径**: `GET /api/system/check-update`

**接口说明**: 检查APP版本更新

---

## 错误码说明

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

## 数据库模型

### User（用户表）
- id: 主键
- username: 用户名
- password_hash: 密码哈希
- nickname: 昵称
- avatar: 头像
- bio: 个人简介
- gender: 性别
- birthday: 生日
- location: 位置
- is_verified: 是否认证
- created_at: 创建时间

### Post（帖子表）
- id: 主键
- user_id: 用户ID
- content: 内容
- images: 图片
- topic: 话题
- created_at: 创建时间
- is_deleted: 是否删除

### Comment（评论表）
- id: 主键
- post_id: 帖子ID
- user_id: 用户ID
- content: 内容
- reply_to_id: 回复ID
- created_at: 创建时间

### Like（点赞表）
- id: 主键
- user_id: 用户ID
- post_id: 帖子ID
- created_at: 创建时间

### Follow（关注表）
- id: 主键
- follower_id: 关注者ID
- followed_id: 被关注者ID
- created_at: 创建时间

### Blacklist（黑名单表）
- id: 主键
- user_id: 用户ID
- blocked_user_id: 被拉黑用户ID
- created_at: 创建时间

### Token（令牌表）
- id: 主键
- user_id: 用户ID
- token: 令牌
- expires_at: 过期时间
- is_valid: 是否有效

### Topic（话题表）
- id: 主键
- name: 话题名称
- posts_count: 帖子数量
- trend: 趋势

### Notification（通知表）
- id: 主键
- user_id: 用户ID
- type: 通知类型
- title: 标题
- content: 内容
- sender_id: 发送者ID
- is_read: 是否已读

---

## 项目结构

```
interest_social_api/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── models/
│   │   ├── __init__.py      # 模型导出
│   │   ├── database.py      # 数据库模型
│   │   └── mock_data.py     # 模拟数据
│   └── routes/
│       ├── __init__.py      # 路由导出
│       ├── auth.py          # 用户认证路由
│       ├── post.py          # 帖子功能路由
│       ├── social.py        # 社交互动路由
│       ├── search.py        # 搜索发现路由
│       ├── home.py          # 首页路由
│       ├── profile.py       # 用户中心路由
│       ├── message.py       # 消息路由
│       ├── news.py          # 新闻路由
│       └── system.py        # 系统路由
├── config/
│   └── __init__.py          # 配置文件
├── uploads/                  # 上传文件目录
├── app.db                    # SQLite数据库
├── requirements.txt          # 依赖列表
├── run.py                    # 启动文件
├── README.md                 # 项目说明
└── API_TEST_DOCUMENT.md      # API测试文档
```

---

## 默认账号

系统初始化时会创建一个默认管理员账号：

- **用户名**: admin
- **密码**: admin123

---

## 更新日志

### v2.0.0 (2024-03-19)

**新增功能**:
1. 用户认证模块
   - 用户注册接口
   - 用户登录接口
   - Token验证接口
   - 用户登出接口
   - 修改密码接口

2. 帖子功能模块
   - 发布帖子接口
   - 删除帖子接口
   - 点赞/取消点赞接口
   - 评论接口
   - 图片上传接口

3. 社交互动模块
   - 关注用户接口
   - 取消关注接口
   - 黑名单管理接口

4. 搜索发现模块
   - 搜索用户接口
   - 搜索帖子接口
   - 搜索话题接口
   - 全局搜索接口

5. 数据持久化
   - SQLite数据库集成
   - Flask-SQLAlchemy ORM模型
   - 数据库自动初始化

**技术改进**:
- 添加JWT认证机制
- 密码加密存储
- 数据库缓存提高性能
- 完善的错误处理

---

## License

MIT License
