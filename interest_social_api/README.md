# 兴趣社交 API

基于 Flask 框架开发的兴趣社交应用后端接口服务。

## 技术栈
- Flask 3.0.0
- SQLite 数据库 (Flask-SQLAlchemy)
- JWT 认证 (Flask-JWT-Extended)
- bcrypt 密码加密

## 功能模块

| 模块 | 功能说明 |
|------|----------|
| **用户认证** | 注册、登录、Token验证、登出、密码加密 |
| **帖子功能** | 发布、删除、点赞、评论、图片上传 |
| **社交互动** | 关注、取关、黑名单 |
| **搜索发现** | 用户搜索、帖子搜索、话题搜索 |

## 快速开始

### 1. 安装依赖
```bash
cd interest_social_api
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python run.py
```
服务启动后访问: http://localhost:5001

### 3. 运行测试
```bash
python test_api.py
```

## API 接口列表

### 认证接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 否 |
| POST | /api/auth/login | 用户登录 | 否 |
| POST | /api/auth/refresh | 刷新Token | 是 |
| POST | /api/auth/logout | 用户登出 | 是 |
| GET | /api/auth/me | 获取用户信息 | 是 |
| POST | /api/auth/change-password | 修改密码 | 是 |

### 帖子接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/posts | 获取帖子列表 | 否 |
| POST | /api/posts | 发布帖子 | 是 |
| GET | /api/posts/<post_id> | 获取帖子详情 | 否 |
| DELETE | /api/posts/<post_id> | 删除帖子 | 是 |
| POST | /api/posts/<post_id>/like | 点赞/取消点赞 | 是 |
| GET | /api/posts/<post_id>/comments | 获取评论列表 | 否 |
| POST | /api/posts/<post_id>/comments | 发布评论 | 是 |
| POST | /api/posts/upload-image | 图片上传 | 是 |

### 社交接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/social/follow/<user_id> | 关注用户 | 是 |
| POST | /api/social/unfollow/<user_id> | 取消关注 | 是 |
| POST | /api/social/block/<user_id> | 拉黑用户 | 是 |
| POST | /api/social/unblock/<user_id> | 取消拉黑 | 是 |
| GET | /api/social/blocklist | 获取黑名单 | 是 |

### 搜索接口
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/search/users | 搜索用户 | 否 |
| GET | /api/search/posts | 搜索帖子 | 否 |
| GET | /api/search/topics | 搜索话题 | 否 |
| GET | /api/search/hot-topics | 热门话题 | 否 |

## 项目结构

```
interest_social_api/
├── app/
│   ├── __init__.py          # Flask应用初始化
│   ├── models/
│   │   └── __init__.py      # 数据库模型
│   └── routes/
│       ├── auth.py          # 认证接口
│       ├── posts.py         # 帖子接口
│       ├── social.py        # 社交接口
│       ├── search.py        # 搜索接口
│       ├── home.py          # 首页接口
│       ├── profile.py       # 用户主页接口
│       ├── message.py       # 消息接口
│       ├── news.py          # 新闻接口
│       └── system.py        # 系统接口
├── config/
│   └── __init__.py          # 配置文件
├── uploads/                 # 上传文件目录
├── app.db                   # SQLite数据库文件
├── requirements.txt         # 依赖列表
├── run.py                   # 应用入口
├── test_api.py              # API测试脚本
└── UNIT_TESTS.md            # 单元测试文档
```

## 请求示例

### 用户注册
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "123456",
    "nickname": "测试用户"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456"
  }'
```

### 发布帖子
```bash
curl -X POST http://localhost:5001/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "content": "今天天气真好！",
    "topic": "#美好生活#",
    "location": "北京市"
  }'
```

## 注意事项

1. **生产环境部署**
   - 请修改 `JWT_SECRET_KEY` 为安全密钥
   - 关闭 `DEBUG` 模式
   - 生产环境建议使用 PostgreSQL 或 MySQL 替代 SQLite

2. **上传文件限制**
   - 支持的图片格式: png, jpg, jpeg, gif
   - 最大文件大小: 16MB

3. **安全提示**
   - Token过期时间默认为1小时
   - 密码使用bcrypt加密存储
   - 生产环境请使用HTTPS
