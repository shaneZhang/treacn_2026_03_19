# 兴趣社交APP API 接口文档

## 基础信息

- **服务地址**: `http://127.0.0.1:5000`
- **数据格式**: JSON
- **编码格式**: UTF-8
- **数据库**: SQLite

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

## 快速开始

### 安装依赖
```bash
cd interest_social_api
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

服务启动后访问 `http://127.0.0.1:5000` 查看所有接口列表。

---

## 认证说明

大部分接口需要Token认证，请在请求头中携带：

```
Authorization: Bearer <token>
```

Token通过登录或注册接口获取，有效期为24小时。

---

## 接口列表

### 一、用户认证模块

#### 1.1 用户注册

**请求路径**: `POST /api/auth/register`

**接口说明**: 注册新用户账号

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

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user | object | 用户信息 |
| token | string | 认证令牌 |
| expires_in | int | 过期时间(秒) |

---

#### 1.2 用户登录

**请求路径**: `POST /api/auth/login`

**接口说明**: 用户登录获取Token

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user | object | 用户信息(含统计数据) |
| token | string | 认证令牌 |
| expires_in | int | 过期时间(秒) |

---

#### 1.3 Token验证

**请求路径**: `GET /api/auth/verify`

**接口说明**: 验证Token是否有效

**认证**: 需要

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user | object | 用户信息 |
| is_valid | bool | 是否有效 |

---

#### 1.4 用户登出

**请求路径**: `POST /api/auth/logout`

**接口说明**: 登出并使Token失效

**认证**: 需要

---

#### 1.5 修改密码

**请求路径**: `POST /api/auth/change-password`

**接口说明**: 修改用户密码

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 旧密码 |
| new_password | string | 是 | 新密码，至少6字符 |

---

### 二、帖子功能模块

#### 2.1 获取帖子列表

**请求路径**: `GET /api/posts`

**接口说明**: 获取帖子列表，支持分页和筛选

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| topic | string | 否 | 话题筛选 |
| user_id | int | 否 | 用户ID筛选 |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| posts | array | 帖子列表 |
| total | int | 总数 |
| page | int | 当前页码 |
| page_size | int | 每页数量 |
| has_more | bool | 是否还有更多 |

---

#### 2.2 发布帖子

**请求路径**: `POST /api/posts`

**接口说明**: 发布新帖子

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 帖子内容，最多5000字符 |
| images | array | 否 | 图片URL数组 |
| topic | string | 否 | 话题 |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| post | object | 帖子详情 |

---

#### 2.3 获取帖子详情

**请求路径**: `GET /api/posts/<post_id>`

**接口说明**: 获取单条帖子详情及评论

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| post_id | int | 是 | 帖子ID |

**响应数据**: 帖子对象，包含comments数组

---

#### 2.4 删除帖子

**请求路径**: `DELETE /api/posts/<post_id>`

**接口说明**: 删除自己的帖子

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| post_id | int | 是 | 帖子ID |

---

#### 2.5 点赞/取消点赞

**请求路径**: `POST /api/posts/<post_id>/like`

**接口说明**: 对帖子点赞或取消点赞

**认证**: 需要

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| is_liked | bool | 是否已点赞 |
| likes_count | int | 点赞总数 |

---

#### 2.6 获取评论列表

**请求路径**: `GET /api/posts/<post_id>/comments`

**接口说明**: 获取帖子的评论列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

---

#### 2.7 发表评论

**请求路径**: `POST /api/posts/<post_id>/comments`

**接口说明**: 对帖子发表评论

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 评论内容，最多1000字符 |
| parent_id | int | 否 | 父评论ID(回复评论时) |

---

#### 2.8 图片上传

**请求路径**: `POST /api/upload/image`

**接口说明**: 上传图片

**认证**: 需要

**请求格式**: multipart/form-data

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | file | 是 | 图片文件，支持png/jpg/jpeg/gif，最大16MB |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| image | object | 图片信息(id, filename, url, size) |

---

### 三、社交互动模块

#### 3.1 关注用户

**请求路径**: `POST /api/social/follow/<user_id>`

**接口说明**: 关注指定用户

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | int | 是 | 要关注的用户ID |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| is_following | bool | 是否已关注 |
| followers_count | int | 对方粉丝数 |
| following_count | int | 当前用户关注数 |

---

#### 3.2 取消关注

**请求路径**: `POST /api/social/unfollow/<user_id>`

**接口说明**: 取消关注指定用户

**认证**: 需要

---

#### 3.3 获取关注列表

**请求路径**: `GET /api/social/following`

**接口说明**: 获取当前用户关注的用户列表

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

---

#### 3.4 获取粉丝列表

**请求路径**: `GET /api/social/followers`

**接口说明**: 获取当前用户的粉丝列表

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

---

#### 3.5 拉黑用户

**请求路径**: `POST /api/social/blacklist/<user_id>`

**接口说明**: 将指定用户加入黑名单

**认证**: 需要

**注意**: 拉黑后会自动取消双方的关注关系

---

#### 3.6 取消拉黑

**请求路径**: `POST /api/social/unblacklist/<user_id>`

**接口说明**: 将指定用户移出黑名单

**认证**: 需要

---

#### 3.7 获取黑名单列表

**请求路径**: `GET /api/social/blacklist`

**接口说明**: 获取当前用户的黑名单列表

**认证**: 需要

---

#### 3.8 检查关注状态

**请求路径**: `GET /api/social/check-follow/<user_id>`

**接口说明**: 检查与指定用户的关注/拉黑状态

**认证**: 需要

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| is_following | bool | 是否已关注 |
| is_blocked | bool | 是否已拉黑对方 |
| is_blocked_by | bool | 是否被对方拉黑 |

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
| page_size | int | 否 | 每页数量，默认20 |

---

#### 4.2 搜索帖子

**请求路径**: `GET /api/search/posts`

**接口说明**: 根据关键词或话题搜索帖子

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| topic | string | 否 | 话题筛选 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

---

#### 4.3 搜索话题

**请求路径**: `GET /api/search/topics`

**接口说明**: 根据关键词搜索话题

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词，为空则返回热门话题 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |

---

#### 4.4 综合搜索

**请求路径**: `GET /api/search/all`

**接口说明**: 综合搜索用户、帖子、话题

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |

**响应数据**:

| 字段 | 类型 | 说明 |
|------|------|------|
| users | array | 用户列表(最多5条) |
| posts | array | 帖子列表(最多5条) |
| topics | array | 话题列表(最多5条) |

---

#### 4.5 获取热门话题

**请求路径**: `GET /api/search/hot-topics`

**接口说明**: 获取热门话题列表

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 数量限制，默认10 |

---

#### 4.6 搜索建议

**请求路径**: `GET /api/search/suggest`

**接口说明**: 获取搜索建议(自动补全)

**请求参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| limit | int | 否 | 数量限制，默认10 |

---

### 五、原有接口

#### 5.1 首页数据

**请求路径**: `GET /api/home`

**接口说明**: 获取APP首页的推荐内容

---

#### 5.2 用户中心

**请求路径**: `GET /api/profile`

**接口说明**: 获取当前登录用户的基本信息

---

#### 5.3 我的帖子

**请求路径**: `GET /api/profile/posts`

**接口说明**: 获取当前用户发布的所有帖子

---

#### 5.4 粉丝列表

**请求路径**: `GET /api/profile/followers`

**接口说明**: 获取当前用户的粉丝列表

---

#### 5.5 关注列表

**请求路径**: `GET /api/profile/following`

**接口说明**: 获取当前用户关注的用户列表

---

#### 5.6 点赞列表

**请求路径**: `GET /api/profile/liked`

**接口说明**: 获取当前用户点赞过的帖子列表

---

#### 5.7 通知列表

**请求路径**: `GET /api/messages/notifications`

**接口说明**: 获取当前用户收到的所有通知

---

#### 5.8 会话列表

**请求路径**: `GET /api/messages/conversations`

**接口说明**: 获取当前用户的所有私信会话列表

---

#### 5.9 私信详情

**请求路径**: `GET /api/messages/private/<user_id>`

**接口说明**: 获取与指定用户的私信聊天记录

---

#### 5.10 发送私信

**请求路径**: `POST /api/messages/send`

**接口说明**: 向指定用户发送私信

---

#### 5.11 检查已读状态

**请求路径**: `GET /api/messages/check-read/<user_id>`

**接口说明**: 检查指定用户发送的消息是否已读

---

#### 5.12 新闻列表

**请求路径**: `GET /api/news`

**接口说明**: 获取新闻列表

---

#### 5.13 新闻详情

**请求路径**: `GET /api/news/<news_id>`

**接口说明**: 获取单条新闻的详细内容

---

#### 5.14 检查更新

**请求路径**: `GET /api/system/check-update`

**接口说明**: 检查APP是否有新版本可用

---

## 数据模型

### User 用户表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户ID |
| username | string | 用户名 |
| password_hash | string | 密码哈希 |
| nickname | string | 昵称 |
| avatar | string | 头像URL |
| bio | string | 个人简介 |
| gender | int | 性别 |
| birthday | string | 生日 |
| location | string | 位置 |
| is_verified | bool | 是否认证 |
| created_at | datetime | 创建时间 |

### Post 帖子表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 帖子ID |
| user_id | int | 用户ID |
| content | text | 内容 |
| images | text | 图片JSON数组 |
| topic | string | 话题 |
| likes_count | int | 点赞数 |
| comments_count | int | 评论数 |
| is_deleted | bool | 是否删除 |
| created_at | datetime | 创建时间 |

### Comment 评论表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评论ID |
| post_id | int | 帖子ID |
| user_id | int | 用户ID |
| content | text | 内容 |
| parent_id | int | 父评论ID |
| created_at | datetime | 创建时间 |

### Like 点赞表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 点赞ID |
| user_id | int | 用户ID |
| post_id | int | 帖子ID |
| created_at | datetime | 创建时间 |

### Follow 关注表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 关注ID |
| follower_id | int | 粉丝ID |
| following_id | int | 被关注者ID |
| created_at | datetime | 创建时间 |

### Blacklist 黑名单表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 记录ID |
| user_id | int | 用户ID |
| blocked_user_id | int | 被拉黑用户ID |
| created_at | datetime | 创建时间 |

### Topic 话题表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 话题ID |
| name | string | 话题名称 |
| description | string | 描述 |
| posts_count | int | 帖子数 |
| created_at | datetime | 创建时间 |

---

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 禁止访问/无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 项目结构

```
interest_social_api/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py      # 数据库模型
│   │   └── mock_data.py     # 模拟数据
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # 用户认证接口
│       ├── posts.py         # 帖子功能接口
│       ├── social.py        # 社交互动接口
│       ├── search.py        # 搜索发现接口
│       ├── home.py          # 首页接口
│       ├── profile.py       # 用户中心接口
│       ├── message.py       # 消息接口
│       ├── news.py          # 新闻接口
│       └── system.py        # 系统接口
├── config/
│   └── __init__.py          # 配置文件
├── uploads/                  # 上传文件目录
├── app.db                    # SQLite数据库
├── init_db.py               # 数据库初始化脚本
├── run.py                   # 启动文件
├── requirements.txt         # 依赖列表
├── README.md                # 项目文档
└── API_TEST.md              # API测试文档
```

---

## 测试账号

初始化数据库后会创建以下测试账号：

| 用户名 | 密码 | 昵称 |
|--------|------|------|
| test_user1 | 123456 | 测试用户1 |
| test_user2 | 123456 | 测试用户2 |
| photographer | 123456 | 摄影大师 |
| traveler | 123456 | 旅行达人 |

---

## 技术栈

- **框架**: Flask 3.0.0
- **数据库**: SQLite + Flask-SQLAlchemy
- **认证**: JWT (PyJWT)
- **跨域**: Flask-Cors
- **密码加密**: Werkzeug

---

## 更多信息

详细的API测试示例请查看 [API_TEST.md](./API_TEST.md)
