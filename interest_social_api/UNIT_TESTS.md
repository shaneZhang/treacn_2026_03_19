# 单元测试文档

## 测试概述
本文档包含兴趣社交API的单元测试说明和示例。

## 测试环境
- 服务器地址: http://localhost:5001
- 测试工具: Python + requests

## 测试用例列表

### 1. 基础接口测试

| 测试用例 | 请求方法 | 路径 | 预期结果 |
|---------|---------|------|---------|
| 根接口测试 | GET | / | 返回200状态码，包含API列表 |

**示例:**
```bash
curl http://localhost:5001/
```

**响应:**
```json
{
  "code": 200,
  "message": "Welcome to Interest Social API",
  "data": {
    "endpoints": [...]
  }
}
```

---

### 2. 用户认证模块

#### 2.1 用户注册
- **方法**: POST
- **路径**: `/api/auth/register`
- **请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "nickname": "测试用户"
}
```
- **预期**: 返回201状态码，包含access_token和user信息

#### 2.2 用户登录
- **方法**: POST
- **路径**: `/api/auth/login`
- **请求体**:
```json
{
  "username": "testuser",
  "password": "123456"
}
```
- **预期**: 返回200状态码，包含access_token和refresh_token

#### 2.3 获取用户信息
- **方法**: GET
- **路径**: `/api/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码和用户详细信息

#### 2.4 用户登出
- **方法**: POST
- **路径**: `/api/auth/logout`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码，登出成功

---

### 3. 帖子功能模块

#### 3.1 发布帖子
- **方法**: POST
- **路径**: `/api/posts`
- **Headers**: `Authorization: Bearer <access_token>`
- **请求体**:
```json
{
  "content": "这是一条测试帖子",
  "images": ["https://picsum.photos/400/400"],
  "topic": "#测试话题#",
  "location": "北京市"
}
```
- **预期**: 返回201状态码和帖子详情

#### 3.2 获取帖子列表
- **方法**: GET
- **路径**: `/api/posts`
- **可选参数**: `page`, `page_size`, `topic`
- **预期**: 返回200状态码和帖子列表

#### 3.3 点赞帖子
- **方法**: POST
- **路径**: `/api/posts/<post_id>/like`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码，is_liked=true

#### 3.4 发布评论
- **方法**: POST
- **路径**: `/api/posts/<post_id>/comments`
- **Headers**: `Authorization: Bearer <access_token>`
- **请求体**:
```json
{
  "content": "很棒的帖子！"
}
```
- **预期**: 返回201状态码和评论详情

---

### 4. 社交互动模块

#### 4.1 关注用户
- **方法**: POST
- **路径**: `/api/social/follow/<user_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码，is_following=true

#### 4.2 拉黑用户
- **方法**: POST
- **路径**: `/api/social/block/<user_id>`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码，操作成功

#### 4.3 获取黑名单
- **方法**: GET
- **路径**: `/api/social/blocklist`
- **Headers**: `Authorization: Bearer <access_token>`
- **预期**: 返回200状态码和黑名单列表

---

### 5. 搜索发现模块

#### 5.1 搜索用户
- **方法**: GET
- **路径**: `/api/search/users?keyword=<关键词>`
- **预期**: 返回200状态码和匹配的用户列表

#### 5.2 搜索帖子
- **方法**: GET
- **路径**: `/api/search/posts?keyword=<关键词>`
- **预期**: 返回200状态码和匹配的帖子列表

#### 5.3 搜索话题
- **方法**: GET
- **路径**: `/api/search/topics?keyword=<关键词>`
- **预期**: 返回200状态码和匹配的话题列表

---

## 运行测试

```bash
cd interest_social_api
python test_api.py
```

## 测试结果示例

```
开始运行 API 测试...
测试服务器: http://localhost:5001

============================================================
测试: 根接口
============================================================
状态码: 200
✓ 根接口测试通过

... (其他测试用例)

============================================================
✓ 所有测试通过!
============================================================
```

## 注意事项
1. 运行测试前请确保服务器已启动
2. 测试会自动创建测试用户和数据
3. Token有效期为1小时，过期后需要重新登录
