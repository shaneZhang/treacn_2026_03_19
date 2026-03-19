from datetime import datetime

current_user = {
    "id": 1001,
    "username": "interest_user",
    "nickname": "兴趣达人",
    "avatar": "https://picsum.photos/200/200?random=0",
    "bio": "热爱生活，热爱分享",
    "gender": 1,
    "birthday": "1995-06-15",
    "location": "北京市朝阳区",
    "followers_count": 3528,
    "following_count": 521,
    "posts_count": 128,
    "likes_count": 15620,
    "is_verified": True,
    "verified_type": "兴趣达人",
    "created_at": "2023-01-15T10:30:00Z"
}

home_banners = [
    {
        "id": 1,
        "title": "春季摄影大赛火热进行中",
        "image": "https://picsum.photos/750/300?random=1",
        "link": "https://example.com/event/1",
        "link_type": "event"
    },
    {
        "id": 2,
        "title": "新功能上线：兴趣圈子等你来",
        "image": "https://picsum.photos/750/300?random=2",
        "link": "https://example.com/circle",
        "link_type": "h5"
    },
    {
        "id": 3,
        "title": "周末户外活动招募中",
        "image": "https://picsum.photos/750/300?random=3",
        "link": "https://example.com/activity/2",
        "link_type": "activity"
    }
]

hot_topics = [
    {"id": 1, "name": "#摄影技巧#", "posts_count": 12580, "trend": "up"},
    {"id": 2, "name": "#旅行日记#", "posts_count": 9870, "trend": "up"},
    {"id": 3, "name": "#美食分享#", "posts_count": 8650, "trend": "stable"},
    {"id": 4, "name": "#户外运动#", "posts_count": 7230, "trend": "up"},
    {"id": 5, "name": "#读书笔记#", "posts_count": 5120, "trend": "down"}
]

recommended_users = [
    {
        "id": 2001,
        "nickname": "摄影大师",
        "avatar": "https://picsum.photos/200/200?random=10",
        "bio": "用镜头记录美好生活",
        "is_following": False,
        "followers_count": 15680
    },
    {
        "id": 2002,
        "nickname": "旅行达人",
        "avatar": "https://picsum.photos/200/200?random=11",
        "bio": "走遍世界每个角落",
        "is_following": True,
        "followers_count": 23450
    },
    {
        "id": 2003,
        "nickname": "美食家",
        "avatar": "https://picsum.photos/200/200?random=12",
        "bio": "发现城市美食",
        "is_following": False,
        "followers_count": 8920
    }
]

recommended_posts = [
    {
        "id": 3001,
        "user_id": 2001,
        "username": "摄影大师",
        "user_avatar": "https://picsum.photos/200/200?random=10",
        "content": "今天的夕阳太美了，随手一拍就是大片！",
        "images": [
            "https://picsum.photos/400/400?random=20",
            "https://picsum.photos/400/400?random=21"
        ],
        "likes_count": 328,
        "comments_count": 45,
        "shares_count": 12,
        "created_at": "2024-03-15T18:30:00Z",
        "is_liked": False,
        "topic": "#摄影技巧#"
    },
    {
        "id": 3002,
        "user_id": 2002,
        "username": "旅行达人",
        "user_avatar": "https://picsum.photos/200/200?random=11",
        "content": "云南之旅，风景如画，期待下次相遇",
        "images": [
            "https://picsum.photos/400/400?random=22",
            "https://picsum.photos/400/400?random=23",
            "https://picsum.photos/400/400?random=24"
        ],
        "likes_count": 892,
        "comments_count": 120,
        "shares_count": 56,
        "created_at": "2024-03-15T15:20:00Z",
        "is_liked": True,
        "topic": "#旅行日记#"
    }
]

interest_categories = [
    {"id": 1, "name": "摄影", "icon": "camera", "posts_count": 25680},
    {"id": 2, "name": "旅行", "icon": "plane", "posts_count": 18920},
    {"id": 3, "name": "美食", "icon": "food", "posts_count": 15430},
    {"id": 4, "name": "运动", "icon": "sport", "posts_count": 12350},
    {"id": 5, "name": "阅读", "icon": "book", "posts_count": 9870},
    {"id": 6, "name": "音乐", "icon": "music", "posts_count": 8650},
    {"id": 7, "name": "绘画", "icon": "art", "posts_count": 6540},
    {"id": 8, "name": "游戏", "icon": "game", "posts_count": 12300}
]

user_posts = [
    {
        "id": 4001,
        "content": "今天天气真好，出去拍照啦！",
        "images": ["https://picsum.photos/400/400?random=30"],
        "likes_count": 56,
        "comments_count": 8,
        "shares_count": 2,
        "created_at": "2024-03-14T10:30:00Z",
        "is_liked": False
    },
    {
        "id": 4002,
        "content": "分享一本好书《活着》，感悟人生",
        "images": [],
        "likes_count": 128,
        "comments_count": 25,
        "shares_count": 10,
        "created_at": "2024-03-12T20:15:00Z",
        "is_liked": True
    },
    {
        "id": 4003,
        "content": "周末户外徒步，累但快乐着",
        "images": [
            "https://picsum.photos/400/400?random=31",
            "https://picsum.photos/400/400?random=32"
        ],
        "likes_count": 245,
        "comments_count": 38,
        "shares_count": 15,
        "created_at": "2024-03-10T16:45:00Z",
        "is_liked": False
    }
]

user_followers = [
    {
        "id": 5001,
        "nickname": "小明",
        "avatar": "https://picsum.photos/200/200?random=40",
        "bio": "热爱摄影",
        "is_following": True,
        "followed_at": "2024-03-01T10:00:00Z"
    },
    {
        "id": 5002,
        "nickname": "小红",
        "avatar": "https://picsum.photos/200/200?random=41",
        "bio": "旅行爱好者",
        "is_following": False,
        "followed_at": "2024-02-28T15:30:00Z"
    },
    {
        "id": 5003,
        "nickname": "小刚",
        "avatar": "https://picsum.photos/200/200?random=42",
        "bio": "美食达人",
        "is_following": True,
        "followed_at": "2024-02-25T09:20:00Z"
    }
]

user_following = [
    {
        "id": 6001,
        "nickname": "大V摄影师",
        "avatar": "https://picsum.photos/200/200?random=50",
        "bio": "专业摄影师",
        "is_following": True,
        "followed_at": "2024-01-15T12:00:00Z"
    },
    {
        "id": 6002,
        "nickname": "旅行家小李",
        "avatar": "https://picsum.photos/200/200?random=51",
        "bio": "环球旅行",
        "is_following": True,
        "followed_at": "2024-01-10T08:30:00Z"
    }
]

user_liked_posts = [
    {
        "id": 7001,
        "user_id": 2001,
        "username": "摄影大师",
        "user_avatar": "https://picsum.photos/200/200?random=10",
        "content": "城市夜景拍摄技巧分享",
        "image": "https://picsum.photos/400/400?random=60",
        "likes_count": 520,
        "created_at": "2024-03-13T19:00:00Z"
    },
    {
        "id": 7002,
        "user_id": 2002,
        "username": "旅行达人",
        "user_avatar": "https://picsum.photos/200/200?random=11",
        "content": "日本旅游全攻略",
        "image": "https://picsum.photos/400/400?random=61",
        "likes_count": 1200,
        "created_at": "2024-03-11T14:30:00Z"
    }
]

notifications = [
    {
        "id": 8001,
        "type": "like",
        "user_id": 2001,
        "user_nickname": "摄影大师",
        "user_avatar": "https://picsum.photos/200/200?random=10",
        "content": "赞了你的帖子",
        "post_id": 4001,
        "is_read": False,
        "created_at": "2024-03-15T20:00:00Z"
    },
    {
        "id": 8002,
        "type": "comment",
        "user_id": 2002,
        "user_nickname": "旅行达人",
        "user_avatar": "https://picsum.photos/200/200?random=11",
        "content": "评论了你的帖子：\"拍得真好！\"",
        "post_id": 4001,
        "is_read": False,
        "created_at": "2024-03-15T19:30:00Z"
    },
    {
        "id": 8003,
        "type": "follow",
        "user_id": 2003,
        "user_nickname": "美食家",
        "user_avatar": "https://picsum.photos/200/200?random=12",
        "content": "关注了你",
        "post_id": None,
        "is_read": True,
        "created_at": "2024-03-15T18:00:00Z"
    },
    {
        "id": 8004,
        "type": "system",
        "user_id": None,
        "user_nickname": "系统通知",
        "user_avatar": "https://picsum.photos/200/200?random=99",
        "content": "欢迎参加春季摄影大赛，丰厚奖品等你来拿！",
        "post_id": None,
        "is_read": True,
        "created_at": "2024-03-14T10:00:00Z"
    }
]

private_messages = [
    {
        "id": 9001,
        "from_user_id": 2001,
        "from_user_nickname": "摄影大师",
        "from_user_avatar": "https://picsum.photos/200/200?random=10",
        "to_user_id": 1001,
        "content": "你好！看了你的照片拍得很不错，可以交流一下吗？",
        "is_read": True,
        "created_at": "2024-03-15T15:30:00Z"
    },
    {
        "id": 9002,
        "from_user_id": 1001,
        "to_user_id": 2001,
        "from_user_nickname": "兴趣达人",
        "from_user_avatar": "https://picsum.photos/200/200?random=0",
        "content": "谢谢夸奖！有机会一起拍照",
        "is_read": True,
        "created_at": "2024-03-15T16:00:00Z"
    },
    {
        "id": 9003,
        "from_user_id": 2002,
        "from_user_nickname": "旅行达人",
        "from_user_avatar": "https://picsum.photos/200/200?random=11",
        "to_user_id": 1001,
        "content": "推荐一个很好的拍摄地点给你",
        "is_read": False,
        "created_at": "2024-03-15T18:30:00Z"
    }
]

conversation_list = [
    {
        "conversation_id": 1,
        "user_id": 2001,
        "nickname": "摄影大师",
        "avatar": "https://picsum.photos/200/200?random=10",
        "last_message": "有机会一起拍照",
        "last_message_time": "2024-03-15T16:00:00Z",
        "unread_count": 0,
        "is_online": True
    },
    {
        "conversation_id": 2,
        "user_id": 2002,
        "nickname": "旅行达人",
        "avatar": "https://picsum.photos/200/200?random=11",
        "last_message": "推荐一个很好的拍摄地点给你",
        "last_message_time": "2024-03-15T18:30:00Z",
        "unread_count": 1,
        "is_online": False
    },
    {
        "conversation_id": 3,
        "user_id": 2003,
        "nickname": "美食家",
        "avatar": "https://picsum.photos/200/200?random=12",
        "last_message": "下次一起吃饭啊",
        "last_message_time": "2024-03-14T20:00:00Z",
        "unread_count": 0,
        "is_online": True
    }
]

news_list = [
    {
        "id": 1,
        "title": "春季摄影大赛正式开启，万元奖金等你来拿",
        "summary": "为广大摄影爱好者提供一个展示才华的平台，本次大赛设置了多个奖项...",
        "image": "https://picsum.photos/400/250?random=70",
        "source": "官方活动",
        "publish_time": "2024-03-15T10:00:00Z",
        "views_count": 5230,
        "comments_count": 128,
        "is_hot": True
    },
    {
        "id": 2,
        "title": "新功能发布：兴趣圈子支持创建话题啦",
        "summary": "现在你可以在自己创建的圈子里发起话题讨论，和志同道合的朋友一起交流...",
        "image": "https://picsum.photos/400/250?random=71",
        "source": "产品动态",
        "publish_time": "2024-03-14T15:30:00Z",
        "views_count": 3560,
        "comments_count": 85,
        "is_hot": False
    },
    {
        "id": 3,
        "title": "摄影师分享：如何用手机拍出专业级照片",
        "summary": "知名摄影师张老师分享手机摄影技巧，让你轻松拍出大片...",
        "image": "https://picsum.photos/400/250?random=72",
        "source": "教程分享",
        "publish_time": "2024-03-13T12:00:00Z",
        "views_count": 8920,
        "comments_count": 256,
        "is_hot": True
    },
    {
        "id": 4,
        "title": "周末去哪儿玩？这几个小众景点值得一去",
        "summary": "远离人挤人，这几个小众景点风景优美，适合周末短途游...",
        "image": "https://picsum.photos/400/250?random=73",
        "source": "旅行攻略",
        "publish_time": "2024-03-12T09:00:00Z",
        "views_count": 6780,
        "comments_count": 142,
        "is_hot": False
    },
    {
        "id": 5,
        "title": "美食教程：在家做出正宗川菜",
        "summary": "川菜大厨教你三道经典川菜做法，在家也能享受美味...",
        "image": "https://picsum.photos/400/250?random=74",
        "source": "美食教程",
        "publish_time": "2024-03-11T18:00:00Z",
        "views_count": 4560,
        "comments_count": 98,
        "is_hot": False
    }
]

app_version = {
    "latest_version": "2.5.0",
    "min_supported_version": "2.0.0",
    "update_content": "1. 优化了首页加载速度\n2. 修复了已知bug\n3. 新增了兴趣圈子功能\n4. 提升了用户体验",
    "download_url": "https://example.com/download",
    "force_update": False,
    "release_date": "2024-03-15"
}
