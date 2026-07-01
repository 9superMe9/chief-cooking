"""
菜谱服务：种子菜谱数据、核心食材识别、食材别名归一化、
基于核心食材的推荐打分（含 strict/flexible/any 模式与保底降级）、
菜/汤分桶推荐与汤类不足提示。
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe, Recommendation
from app.models.user import User
from app.schemas.recipe import RecommendationRequest, RecommendationResponse

# AI 生成菜谱的标记，存入 ai_reason 字段用于识别和清理
AI_RECIPE_MARKER = "__AI_GENERATED__"


MOCK_RECIPES = [
    {
        "name": "番茄炒蛋",
        "description": "经典家常菜，酸甜可口，营养均衡",
        "ingredients": ["番茄", "鸡蛋", "葱花"],
        "steps": ["番茄切块", "鸡蛋打散", "热锅炒蛋盛出", "番茄炒软加蛋", "调味出锅"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "蛋炒饭",
        "description": "粒粒分明，香气四溢，快手主食",
        "ingredients": ["米饭", "鸡蛋", "葱花", "火腿肠"],
        "steps": ["鸡蛋打散炒熟", "加入米饭翻炒", "加入火腿丁", "调味出锅"],
        "cooking_time": "10分钟",
        "servings": "1人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "主食",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "番茄蛋汤",
        "description": "清淡鲜美，营养丰富，老少皆宜",
        "ingredients": ["番茄", "鸡蛋", "葱花"],
        "steps": ["番茄切块炒软", "加水煮沸", "淋入蛋液", "调味出锅"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "汤羹",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "鸡蛋羹",
        "description": "嫩滑爽口，入口即化，适合老人小孩",
        "ingredients": ["鸡蛋", "温水"],
        "steps": ["鸡蛋打散", "加入1.5倍温水", "过筛去浮沫", "盖保鲜膜蒸10分钟"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "家常菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "西红柿鸡蛋面",
        "description": "家常美味，温暖身心，快手主食",
        "ingredients": ["番茄", "鸡蛋", "面条", "葱花"],
        "steps": ["番茄炒蛋备用", "煮面条", "加入番茄鸡蛋卤"],
        "cooking_time": "20分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "主食",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "青椒炒蛋",
        "description": "鲜香可口，下饭神器",
        "ingredients": ["青椒", "鸡蛋", "蒜末"],
        "steps": ["青椒切丝", "鸡蛋打散炒熟", "爆香蒜末", "加入青椒鸡蛋"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "红烧肉",
        "description": "肥而不腻，入口即化，经典硬菜",
        "ingredients": ["五花肉", "生姜", "大葱", "冰糖"],
        "steps": ["五花肉切块焯水", "炒糖色", "加入肉块翻炒", "加水炖煮", "收汁出锅"],
        "cooking_time": "60分钟",
        "servings": "4人份",
        "taste": "重口",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["高油", "高糖"],
        "image_url": "",
    },
    {
        "name": "清蒸鱼",
        "description": "鲜嫩爽滑，保留营养，清淡健康",
        "ingredients": ["鱼", "生姜", "大葱", "蒸鱼豉油"],
        "steps": ["鱼处理干净", "放姜片葱段", "蒸8-10分钟", "淋蒸鱼豉油"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["鱼刺"],
        "image_url": "",
    },
    {
        "name": "宫保鸡丁",
        "description": "酸甜微辣，花生香脆，下饭经典",
        "ingredients": ["鸡肉", "花生", "干辣椒", "葱段"],
        "steps": ["鸡肉切丁腌制", "炸花生米", "爆香调料", "加入鸡丁翻炒"],
        "cooking_time": "25分钟",
        "servings": "3人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["微辣", "坚果"],
        "image_url": "",
    },
    {
        "name": "土豆丝",
        "description": "酸辣爽口，开胃下饭，家常菜必备",
        "ingredients": ["土豆", "青椒", "干辣椒", "蒜末"],
        "steps": ["土豆切丝泡水", "爆香调料", "加入土豆丝快炒", "调味出锅"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "炒青菜",
        "description": "翠绿爽口，简单健康，清肠解腻",
        "ingredients": ["青菜", "蒜末"],
        "steps": ["青菜洗净切段", "爆香蒜末", "加入青菜快炒", "调味出锅"],
        "cooking_time": "8分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "麻婆豆腐",
        "description": "麻辣鲜香，嫩滑入味，川菜经典",
        "ingredients": ["豆腐", "肉末", "豆瓣酱", "花椒"],
        "steps": ["豆腐切块焯水", "炒肉末", "加豆瓣酱", "加水炖煮", "勾芡出锅"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "豆制品",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "糖醋排骨",
        "description": "酸甜适口，外酥里嫩，宴客必备",
        "ingredients": ["排骨", "冰糖", "醋", "生姜"],
        "steps": ["排骨焯水", "炒糖色", "加入排骨翻炒", "加水炖煮", "收汁"],
        "cooking_time": "40分钟",
        "servings": "4人份",
        "taste": "家常",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["高糖"],
        "image_url": "",
    },
    {
        "name": "酸菜鱼",
        "description": "酸辣开胃，鱼肉嫩滑，经典川菜",
        "ingredients": ["鱼", "酸菜", "干辣椒", "花椒"],
        "steps": ["鱼片腌制", "炒酸菜", "加水煮沸", "滑入鱼片", "热油淋香"],
        "cooking_time": "30分钟",
        "servings": "4人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "海鲜",
        "risk_tags": ["微辣", "鱼刺"],
        "image_url": "",
    },
    {
        "name": "蒜蓉西兰花",
        "description": "清脆爽口，营养丰富，健身首选",
        "ingredients": ["西兰花", "蒜末"],
        "steps": ["西兰花切小朵焯水", "爆香蒜末", "加入西兰花翻炒", "调味出锅"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "回锅肉",
        "description": "肥而不腻，酱香浓郁，川菜经典",
        "ingredients": ["五花肉", "青椒", "蒜苗", "豆瓣酱"],
        "steps": ["五花肉煮熟切片", "爆香豆瓣酱", "加入肉片翻炒", "加入配菜"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "重口",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["高油", "微辣"],
        "image_url": "",
    },
    {
        "name": "蒜蓉虾",
        "description": "鲜美多汁，蒜香浓郁，宴客硬菜",
        "ingredients": ["虾", "蒜末", "葱花"],
        "steps": ["虾开背去虾线", "铺蒜末", "蒸5分钟", "淋热油"],
        "cooking_time": "10分钟",
        "servings": "3人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "炒土豆丝",
        "description": "酸辣脆爽，开胃下饭",
        "ingredients": ["土豆", "干辣椒", "醋"],
        "steps": ["土豆切丝泡水", "爆香辣椒", "快炒土豆丝", "淋醋调味"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "酸辣汤",
        "description": "酸辣开胃，暖身驱寒",
        "ingredients": ["豆腐", "木耳", "鸡蛋", "醋"],
        "steps": ["食材切好", "加水煮沸", "勾芡", "淋蛋液", "加醋调味"],
        "cooking_time": "15分钟",
        "servings": "3人份",
        "taste": "微辣",
        "difficulty": "简单",
        "category": "汤羹",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "鱼香肉丝",
        "description": "酸甜微辣，香气扑鼻，下饭神器",
        "ingredients": ["猪肉", "胡萝卜", "木耳", "青椒"],
        "steps": ["肉丝腌制", "配菜切丝", "炒肉丝", "调鱼香汁", "混合翻炒"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "西兰花炒虾仁",
        "description": "营养均衡，清淡鲜美，健身餐首选",
        "ingredients": ["西兰花", "虾仁", "蒜末"],
        "steps": ["西兰花焯水", "虾仁腌制", "爆香蒜末", "混合快炒"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "肉末茄子",
        "description": "软烂入味，酱香浓郁，下饭必备",
        "ingredients": ["茄子", "肉末", "蒜末", "豆瓣酱"],
        "steps": ["茄子切块煎软", "炒肉末", "加调料", "加入茄子炖煮"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "家常",
        "difficulty": "中等",
        "category": "素菜",
        "risk_tags": ["高油"],
        "image_url": "",
    },
    {
        "name": "凉拌黄瓜",
        "description": "清爽可口，开胃解腻，夏日必备",
        "ingredients": ["黄瓜", "蒜末", "辣椒油"],
        "steps": ["黄瓜拍碎", "加入调料", "拌匀冷藏"],
        "cooking_time": "5分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "凉菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "青椒土豆丝",
        "description": "爽脆可口，简单下饭",
        "ingredients": ["土豆", "青椒", "蒜末"],
        "steps": ["土豆青椒切丝", "爆香蒜末", "快炒", "调味"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "家常",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "蚝油生菜",
        "description": "翠绿鲜嫩，蚝油鲜香",
        "ingredients": ["生菜", "蒜末", "蚝油"],
        "steps": ["生菜焯水", "爆香蒜末", "加蚝油", "淋在生菜上"],
        "cooking_time": "8分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "清蒸排骨",
        "description": "鲜嫩多汁，原汁原味，清淡健康",
        "ingredients": ["排骨", "生姜", "葱段"],
        "steps": ["排骨焯水", "放姜片葱段", "蒸30分钟", "调味"],
        "cooking_time": "35分钟",
        "servings": "3人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "西红柿炖牛腩",
        "description": "软烂入味，汤浓肉香，经典硬菜",
        "ingredients": ["牛腩", "番茄", "胡萝卜", "生姜"],
        "steps": ["牛腩切块焯水", "炒香", "加水炖煮", "加入番茄胡萝卜"],
        "cooking_time": "90分钟",
        "servings": "4人份",
        "taste": "家常",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": ["高嘌呤"],
        "image_url": "",
    },
    {
        "name": "凉拌番茄",
        "description": "酸甜可口，清爽解暑",
        "ingredients": ["番茄", "白糖"],
        "steps": ["番茄切块", "撒白糖", "静置10分钟"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "凉菜",
        "risk_tags": ["高糖"],
        "image_url": "",
    },
    {
        "name": "黄瓜炒鸡蛋",
        "description": "清爽可口，简单健康",
        "ingredients": ["黄瓜", "鸡蛋", "葱花"],
        "steps": ["鸡蛋打散炒熟", "黄瓜切片", "混合快炒", "调味"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "素菜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "炒虾仁",
        "description": "鲜美嫩滑，简单快手",
        "ingredients": ["虾仁", "黄瓜", "胡萝卜"],
        "steps": ["虾仁腌制", "配菜切片", "快炒虾仁", "加入配菜"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    # ---- 扩充菜谱：补齐常见家常菜，重点补牛肉/青椒/猪肉组合 ----
    {
        "name": "青椒炒牛肉",
        "description": "牛肉滑嫩，青椒脆爽，下饭神器",
        "ingredients": ["牛肉", "青椒", "生抽", "淀粉"],
        "steps": ["牛肉切片加生抽淀粉腌制", "青椒切块", "大火滑炒牛肉", "加入青椒翻炒"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "青椒肉丝",
        "description": "经典下饭菜，肉丝入味青椒脆",
        "ingredients": ["猪肉", "青椒", "生抽", "淀粉"],
        "steps": ["猪肉切丝腌制", "青椒切丝", "滑炒肉丝", "加青椒丝翻炒"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "番茄牛腩",
        "description": "牛肉软烂，番茄酸甜，汤汁拌饭一绝",
        "ingredients": ["牛肉", "番茄", "土豆", "生姜"],
        "steps": ["牛肉切块焯水", "番茄切块炒出汁", "加牛肉炖煮", "放土豆炖软"],
        "cooking_time": "60分钟",
        "servings": "3人份",
        "taste": "酸甜",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "芹菜炒牛肉",
        "description": "清香脆嫩，牛肉滑嫩",
        "ingredients": ["牛肉", "芹菜", "生抽"],
        "steps": ["牛肉切丝腌制", "芹菜切段", "滑炒牛肉", "加芹菜快炒"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "洋葱炒牛肉",
        "description": "洋葱甜香，牛肉嫩滑",
        "ingredients": ["牛肉", "洋葱", "生抽"],
        "steps": ["牛肉切片腌制", "洋葱切丝", "滑炒牛肉", "加洋葱翻炒"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "土豆烧牛肉",
        "description": "牛肉软烂土豆绵软，浓香入味",
        "ingredients": ["牛肉", "土豆", "胡萝卜", "生抽"],
        "steps": ["牛肉焯水", "炒糖色", "加牛肉土豆胡萝卜炖煮", "收汁"],
        "cooking_time": "50分钟",
        "servings": "3人份",
        "taste": "咸鲜",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "肉末豆腐",
        "description": "豆腐嫩滑肉末香，拌饭神器",
        "ingredients": ["猪肉", "豆腐", "豆瓣酱", "葱花"],
        "steps": ["猪肉剁末", "豆腐切块", "炒肉末", "加豆腐烧入味"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "豆制品",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "番茄鸡蛋面",
        "description": "酸甜开胃，一碗管饱",
        "ingredients": ["番茄", "鸡蛋", "面条"],
        "steps": ["炒鸡蛋盛出", "炒番茄出汁", "加水煮面", "放鸡蛋"],
        "cooking_time": "15分钟",
        "servings": "1人份",
        "taste": "酸甜",
        "difficulty": "简单",
        "category": "主食",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "黄瓜炒肉片",
        "description": "清爽脆嫩，快手小炒",
        "ingredients": ["猪肉", "黄瓜", "生抽"],
        "steps": ["猪肉切片腌制", "黄瓜切片", "滑炒肉片", "加黄瓜翻炒"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "鸡蛋炒饭",
        "description": "粒粒分明，蛋香四溢",
        "ingredients": ["鸡蛋", "米饭", "葱花"],
        "steps": ["鸡蛋打散", "热油炒蛋", "加米饭翻炒", "撒葱花"],
        "cooking_time": "10分钟",
        "servings": "1人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "主食",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "紫菜蛋花汤",
        "description": "清淡鲜美，1分钟快手汤",
        "ingredients": ["鸡蛋", "紫菜", "葱花"],
        "steps": ["水烧开", "放紫菜", "淋蛋液", "撒葱花"],
        "cooking_time": "5分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "汤类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "醋溜白菜",
        "description": "酸爽开胃，清脆爽口",
        "ingredients": ["白菜", "醋", "干辣椒"],
        "steps": ["白菜切块", "热油爆香辣椒", "大火炒白菜", "烹醋调味"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "酸甜",
        "difficulty": "简单",
        "category": "蔬菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    # ---- 三文鱼系列 ----
    {
        "name": "香煎三文鱼",
        "description": "外焦里嫩，金黄诱人，营养丰富",
        "ingredients": ["三文鱼", "柠檬", "黑胡椒"],
        "steps": ["三文鱼擦干水分", "撒盐和黑胡椒", "热锅少油煎至金黄", "挤柠檬汁出锅"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "三文鱼炒饭",
        "description": "粒粒分明，三文鱼鲜香，营养一锅端",
        "ingredients": ["三文鱼", "米饭", "鸡蛋", "葱花"],
        "steps": ["三文鱼切丁煎香", "鸡蛋炒散", "加米饭翻炒", "放三文鱼丁调味"],
        "cooking_time": "15分钟",
        "servings": "1人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "主食",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "蒜香三文鱼",
        "description": "蒜香浓郁，鱼肉嫩滑，快手硬菜",
        "ingredients": ["三文鱼", "蒜末", "生抽"],
        "steps": ["三文鱼切块", "蒜末爆香", "放入三文鱼煎炒", "淋生抽调味"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "三文鱼头豆腐汤",
        "description": "汤白如奶，鲜美滋补，秋冬暖身",
        "ingredients": ["三文鱼", "豆腐", "生姜", "葱段"],
        "steps": ["鱼头煎至两面金黄", "加开水大火煮", "放豆腐炖煮", "调味撒葱"],
        "cooking_time": "30分钟",
        "servings": "3人份",
        "taste": "清淡",
        "difficulty": "中等",
        "category": "汤类",
        "risk_tags": ["鱼刺"],
        "image_url": "",
    },
    {
        "name": "三文鱼刺身",
        "description": "原汁原味，鲜甜软糯，日式经典",
        "ingredients": ["三文鱼", "芥末", "酱油"],
        "steps": ["三文鱼冷冻杀菌后解冻", "逆纹切薄片", "配芥末酱油食用"],
        "cooking_time": "10分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "凉菜",
        "risk_tags": ["生食"],
        "image_url": "",
    },
    # ---- 更多家常菜扩充 ----
    {
        "name": "可乐鸡翅",
        "description": "甜香入骨，嫩滑多汁，老少皆宜",
        "ingredients": ["鸡翅", "可乐", "生姜", "生抽"],
        "steps": ["鸡翅划口焯水", "煎至两面金黄", "加可乐和生抽", "收汁出锅"],
        "cooking_time": "25分钟",
        "servings": "3人份",
        "taste": "甜咸",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": ["高糖"],
        "image_url": "",
    },
    {
        "name": "干煸四季豆",
        "description": "干香入味，脆嫩爽口，下饭神器",
        "ingredients": ["四季豆", "肉末", "干辣椒", "蒜末"],
        "steps": ["四季豆摘段", "干煸至虎皮", "炒肉末", "加调料翻炒"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "素菜",
        "risk_tags": ["微辣"],
        "image_url": "",
    },
    {
        "name": "鱼香茄子",
        "description": "酱香浓郁，茄子软烂，川菜经典",
        "ingredients": ["茄子", "肉末", "豆瓣酱", "蒜末"],
        "steps": ["茄子切条煎软", "炒肉末出油", "加豆瓣酱", "放入茄子烧入味"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "微辣",
        "difficulty": "中等",
        "category": "素菜",
        "risk_tags": ["高油", "微辣"],
        "image_url": "",
    },
    {
        "name": "葱爆羊肉",
        "description": "葱香浓郁，羊肉嫩滑，北方经典",
        "ingredients": ["羊肉", "大葱", "生抽"],
        "steps": ["羊肉切片腌制", "大葱切段", "大火爆炒羊肉", "加葱段翻炒"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "虾仁豆腐",
        "description": "鲜嫩爽滑，高蛋白低脂，老少皆宜",
        "ingredients": ["虾仁", "豆腐", "葱花"],
        "steps": ["豆腐切块", "虾仁腌制", "烧豆腐", "放虾仁煮熟调味"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "清淡",
        "difficulty": "简单",
        "category": "豆制品",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "番茄龙利鱼",
        "description": "酸甜开胃，鱼肉嫩滑，无刺放心吃",
        "ingredients": ["龙利鱼", "番茄", "蒜末"],
        "steps": ["龙利鱼切块腌制", "番茄炒出汁", "加水煮开", "放入鱼肉煮熟"],
        "cooking_time": "20分钟",
        "servings": "2人份",
        "taste": "酸甜",
        "difficulty": "简单",
        "category": "海鲜",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "蒜薹炒肉",
        "description": "蒜薹脆嫩，肉丝入味，春季时令菜",
        "ingredients": ["猪肉", "蒜薹", "生抽"],
        "steps": ["猪肉切丝腌制", "蒜薹切段", "滑炒肉丝", "加蒜薹翻炒"],
        "cooking_time": "12分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "地三鲜",
        "description": "东北经典，土豆茄子青椒完美组合",
        "ingredients": ["土豆", "茄子", "青椒", "蒜末"],
        "steps": ["土豆茄子切块炸软", "调酱汁", "所有食材烧在一起", "收汁出锅"],
        "cooking_time": "20分钟",
        "servings": "3人份",
        "taste": "咸鲜",
        "difficulty": "中等",
        "category": "素菜",
        "risk_tags": ["高油"],
        "image_url": "",
    },
    {
        "name": "木须肉",
        "description": "荤素搭配，木耳鸡蛋黄花菜，家常经典",
        "ingredients": ["猪肉", "鸡蛋", "木耳", "黄瓜"],
        "steps": ["鸡蛋炒散盛出", "炒肉片", "加木耳黄瓜", "放鸡蛋翻炒调味"],
        "cooking_time": "15分钟",
        "servings": "2人份",
        "taste": "咸鲜",
        "difficulty": "简单",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
    {
        "name": "蒜蓉粉丝蒸虾",
        "description": "蒜香粉丝吸满鲜汁，宴客硬菜",
        "ingredients": ["虾", "粉丝", "蒜末", "葱花"],
        "steps": ["粉丝泡软铺底", "虾开背摆在粉丝上", "铺蒜末", "蒸6分钟淋油"],
        "cooking_time": "15分钟",
        "servings": "3人份",
        "taste": "咸鲜",
        "difficulty": "中等",
        "category": "海鲜",
        "risk_tags": ["海鲜过敏"],
        "image_url": "",
    },
    {
        "name": "白切鸡",
        "description": "皮爽肉滑，原汁原味，粤菜经典",
        "ingredients": ["鸡肉", "生姜", "大葱"],
        "steps": ["整鸡煮20分钟", "冰水浸泡", "斩块装盘", "蘸料食用"],
        "cooking_time": "30分钟",
        "servings": "4人份",
        "taste": "清淡",
        "difficulty": "中等",
        "category": "肉类",
        "risk_tags": [],
        "image_url": "",
    },
]

# 食材别名表：键为标准名，值为该标准名对应的所有别名
# 推荐匹配时，用户输入的别名会归一化到标准名
INGREDIENT_ALIASES = {
    "牛肉": ["牛腩", "牛里脊", "牛腱", "牛排", "肥牛"],
    "猪肉": ["五花肉", "里脊肉", "瘦肉"],
    "鸡肉": ["鸡腿", "鸡胸", "鸡翅", "鸡丁"],
    "羊肉": ["羊腿", "羊排"],
    "番茄": ["西红柿"],
    "土豆": ["马铃薯"],
    "青菜": ["小白菜", "油菜", "上海青"],
    "虾仁": ["虾", "基围虾"],
    "白菜": ["大白菜", "娃娃菜"],
    "三文鱼": ["鲑鱼", "salmon"],
    "龙利鱼": ["巴沙鱼", "龙利柳"],
    "鸡翅": ["鸡中翅", "翅中"],
    "蒜薹": ["蒜苗", "蒜毫"],
    "四季豆": ["芸豆", "豆角"],
}

# 反向查找表：别名 -> 标准名（启动时构建）
_ALIAS_TO_STANDARD = {}
for _std, _aliases in INGREDIENT_ALIASES.items():
    _ALIAS_TO_STANDARD[_std] = _std
    for _a in _aliases:
        _ALIAS_TO_STANDARD[_a] = _std


def _normalize_ingredient(name: str) -> str:
    """食材名归一化：别名映射到标准名（如 牛腩→牛肉）"""
    return _ALIAS_TO_STANDARD.get(name, name)


def _normalize_ingredients(names: List[str]) -> List[str]:
    """批量归一化食材名"""
    return [_normalize_ingredient(n) for n in names]


def _is_soup(recipe) -> bool:
    """判断是否为汤类菜谱（category 含'汤'字）"""
    cat = getattr(recipe, "category", "") or ""
    return "汤" in cat


RISK_RULES = {
    "老人": ["高油", "高糖", "微辣", "重口"],
    "小孩": ["微辣", "重口", "鱼刺", "坚果"],
    "健身": ["高油", "高糖"],
    "少盐": ["高盐"],
    "少糖": ["高糖"],
    "少油": ["高油"],
    "不吃辣": ["微辣", "重口"],
    "不吃葱蒜": ["葱", "蒜"],
}

# 调味料/辅料白名单：这些不算核心食材，缺失不影响做菜
PANTRY_SEASONINGS = {
    "盐", "油", "酱油", "生抽", "老抽", "醋", "糖", "料酒",
    "葱花", "蒜末", "蒜", "蒜蓉", "生姜", "姜", "大葱", "葱段", "葱",
    "豆瓣酱", "花椒", "干辣椒", "蚝油", "蒸鱼豉油", "淀粉",
    "胡椒粉", "五香粉", "辣椒油", "香油", "鸡精", "味精",
    "冰糖", "白糖", "食盐", "食用油", "菜籽油", "花生油",
    "八角", "桂皮", "香叶", "芝麻", "白芝麻",
    "温水", "水", "热水", "清水",
}


def _core_ingredients(recipe_ingredients: List[str]) -> List[str]:
    """剔除调味料/辅料，返回核心食材（主料）"""
    return [i for i in recipe_ingredients if i not in PANTRY_SEASONINGS]


class RecipeService:
    @staticmethod
    async def get_all_recipes(db: AsyncSession) -> List[Recipe]:
        result = await db.execute(select(Recipe))
        return result.scalars().all()

    @staticmethod
    async def get_recipe_by_id(db: AsyncSession, recipe_id: str) -> Optional[Recipe]:
        result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
        return result.scalars().first()

    @staticmethod
    async def cleanup_ai_recipes(db: AsyncSession) -> int:
        """清理超过 1 小时的 AI 生成菜谱，返回删除数量"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        result = await db.execute(
            delete(Recipe).where(
                Recipe.ai_reason == AI_RECIPE_MARKER,
                Recipe.created_at < cutoff,
            )
        )
        if result.rowcount and result.rowcount > 0:
            await db.commit()
        return result.rowcount or 0

    @staticmethod
    async def ensure_mock_recipes(db: AsyncSession) -> None:
        # 先清理过期的 AI 生成菜谱（超过 1 小时）
        await RecipeService.cleanup_ai_recipes(db)
        existing_recipes = await RecipeService.get_all_recipes(db)
        existing_names = {r.name for r in existing_recipes}

        # 修复历史数据：把仍指向内部文生图接口的 image_url 清空
        dirty = False
        for r in existing_recipes:
            if r.image_url and "trae-api-cn.mchost.guru" in r.image_url:
                r.image_url = ""
                dirty = True

        # 增量添加新菜谱（数据库中不存在的）
        new_added = False
        for recipe_data in MOCK_RECIPES:
            if recipe_data["name"] not in existing_names:
                recipe = Recipe(
                    id=str(uuid.uuid4()),
                    **recipe_data,
                )
                db.add(recipe)
                new_added = True

        if dirty or new_added:
            await db.commit()

    @staticmethod
    def calculate_match_score(recipe: Recipe, user_ingredients: List[str]) -> int:
        """旧版评分（保留兼容）：交集数量"""
        if not user_ingredients:
            return 0
        recipe_ingredients = set(recipe.ingredients)
        user_ingredient_set = set(user_ingredients)
        matched = len(recipe_ingredients.intersection(user_ingredient_set))
        return matched

    @staticmethod
    def calculate_match_score_v2(
        matched_count: int, missing_count: int, core_count: int
    ) -> float:
        """
        v2 评分模型：基于核心食材的覆盖率 + 完全匹配奖励 - 缺失惩罚
        - matched_count: 命中的核心食材数
        - missing_count: 缺失的核心食材数
        - core_count: 菜谱核心食材总数
        """
        if core_count == 0:
            return 0
        coverage = matched_count / core_count  # 覆盖率 0-1
        score = matched_count * 10              # 命中加分
        score += coverage * 30                  # 覆盖率奖励
        score -= missing_count * 5              # 缺失惩罚
        if missing_count == 0:                  # 完全匹配额外奖励
            score += 50
        return score

    @staticmethod
    def get_risk_tags(recipe: Recipe, preferences: Optional[dict]) -> List[str]:
        risk_tags = recipe.risk_tags if hasattr(recipe, 'risk_tags') and recipe.risk_tags else []
        
        if preferences:
            people_tags = preferences.get("peopleTags", [])
            restrictions = preferences.get("restrictions", [])
            
            all_tags = people_tags + restrictions
            
            for tag in all_tags:
                if tag in RISK_RULES:
                    for risk in RISK_RULES[tag]:
                        if risk in risk_tags:
                            return risk_tags
            
        return risk_tags

    @staticmethod
    def is_recipe_suitable(recipe: Recipe, preferences: Optional[dict]) -> bool:
        if not preferences:
            return True
            
        risk_tags = recipe.risk_tags if hasattr(recipe, 'risk_tags') and recipe.risk_tags else []
        
        people_tags = preferences.get("peopleTags", [])
        restrictions = preferences.get("restrictions", [])
        
        for tag in people_tags + restrictions:
            if tag in RISK_RULES:
                for risk in RISK_RULES[tag]:
                    if risk in risk_tags:
                        return False
        
        return True

    @staticmethod
    async def recommend_recipes(
        db: AsyncSession,
        user_ingredients: List[str],
        preferences: Optional[dict] = None,
        limit: int = 5,
        mode: str = "strict",
    ) -> Tuple[List, bool, str]:
        """
        基于核心食材的推荐，支持菜/汤分桶。
        mode: strict(只推齐全) / flexible(允许缺1-2样) / any(任意)
        preferences.dishCount: 菜数（默认用 limit 推算）
        preferences.soupCount: 汤数（默认0）
        返回: (recipes, downgraded, soup_warning)
        """
        await RecipeService.ensure_mock_recipes(db)
        all_recipes = await RecipeService.get_all_recipes(db)

        def _score_and_filter(recipes_list, filter_mode):
            """返回按分数排序的全部候选（已应用偏好过滤），不截断"""
            user_set = set(_normalize_ingredients(user_ingredients or []))
            scored = []
            for recipe in recipes_list:
                if not RecipeService.is_recipe_suitable(recipe, preferences):
                    continue
                core = _core_ingredients(_normalize_ingredients(recipe.ingredients or []))
                if not core:
                    continue
                matched = set(core).intersection(user_set)
                missing = set(core) - user_set
                if not matched:
                    continue
                missing_count = len(missing)
                if filter_mode == "strict" and missing_count > 0:
                    continue
                elif filter_mode == "flexible" and missing_count > 2:
                    continue
                score = RecipeService.calculate_match_score_v2(
                    len(matched), missing_count, len(core)
                )
                # 加入较大随机扰动（±15），让分数相近的菜谱每次排序不同，
                # "重新推荐"时能出现不同菜谱组合，完全匹配的高分菜谱仍优先。
                score += random.uniform(-15, 15)
                scored.append((recipe, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            # 偏好软排序：口味/时间/难度作为加分项而非硬过滤，
            # 避免食材较少时候选被过滤到不足推荐数量。
            # 健康/禁忌(risk_tags)仍由 is_recipe_suitable 硬过滤。
            if preferences:
                taste = preferences.get("taste")
                cooking_time = preferences.get("cookingTime")
                difficulty = preferences.get("difficulty")
                if taste and taste != "":
                    scored = [(r, s + (15 if r.taste == taste else 0)) for r, s in scored]
                if cooking_time and cooking_time != "":
                    try:
                        max_time = int(str(cooking_time).replace("分钟", ""))
                        scored = [
                            (r, s + (10 if int(str(r.cooking_time).replace("分钟", "")) <= max_time else 0))
                            for r, s in scored
                        ]
                    except (ValueError, AttributeError):
                        pass
                if difficulty and difficulty != "":
                    scored = [(r, s + (15 if r.difficulty == difficulty else 0)) for r, s in scored]
                scored.sort(key=lambda x: x[1], reverse=True)
            return [r for r, s in scored]

        def _pick_by_bucket(candidates):
            """按菜/汤分桶取：dishCount 道非汤 + soupCount 道汤
            从 top N*2 候选池中随机抽样，让"重新推荐"每次出现不同菜谱组合。"""
            soups = [r for r in candidates if _is_soup(r)]
            dishes = [r for r in candidates if not _is_soup(r)]

            def _sample_pool(pool, n):
                """从候选池前 n*2 名中随机抽 n 道，保证相关性同时增加多样性"""
                if n <= 0 or not pool:
                    return []
                pool_size = min(len(pool), max(n * 2, n + 2))
                top_pool = pool[:pool_size]
                if len(top_pool) <= n:
                    return top_pool
                return random.sample(top_pool, n)

            picked_dishes = _sample_pool(dishes, dish_count)
            picked_soups = _sample_pool(soups, soup_count)
            picked = picked_dishes + picked_soups
            # 汤不足时，用菜补足总数
            if len(picked_soups) < soup_count:
                shortfall = soup_count - len(picked_soups)
                remaining = [d for d in dishes if d not in picked_dishes]
                picked += remaining[:shortfall]
            return picked, len(soups)

        # 解析菜数/汤数（显式传 0 也生效，未传则用默认值）
        dish_count = limit
        soup_count = 0
        if preferences:
            if "dishCount" in preferences:
                try:
                    dish_count = int(preferences["dishCount"])
                except (ValueError, TypeError):
                    pass
            if "soupCount" in preferences:
                try:
                    soup_count = int(preferences["soupCount"])
                except (ValueError, TypeError):
                    pass

        total_wanted = dish_count + soup_count
        candidates = _score_and_filter(all_recipes, mode)
        downgraded = False

        # 保底降级：strict 有食材但候选为 0 时，自动放宽到 flexible
        if mode == "strict" and not candidates and user_ingredients:
            candidates = _score_and_filter(all_recipes, "flexible")
            downgraded = bool(candidates)

        # 数量补足：候选不足要求数量时，放宽到 any 模式补足，保证推荐数量
        if len(candidates) < total_wanted and user_ingredients and mode != "any":
            wider = _score_and_filter(all_recipes, "any")
            existing_ids = {r.id for r in candidates}
            for r in wider:
                if len(candidates) >= total_wanted:
                    break
                if r.id not in existing_ids:
                    candidates.append(r)
                    existing_ids.add(r.id)
                    downgraded = True

        results, available_soups = _pick_by_bucket(candidates)
        results = results[:total_wanted]

        # 汤类不足提示
        soup_warning = ""
        if soup_count > 0 and available_soups < soup_count:
            if available_soups == 0:
                soup_warning = "当前食材做不出汤，已用菜补足，可补充食材后再试"
            else:
                soup_warning = f"只能做出 {available_soups} 道汤，缺 {soup_count - available_soups} 道，已用菜补足"

        return results, downgraded, soup_warning

    @staticmethod
    async def save_recommendation(
        db: AsyncSession,
        user_id: Optional[str],
        session_id: Optional[str],
        recipe_ids: List[str],
    ) -> Recommendation:
        recommendation = Recommendation(
            user_id=user_id,
            session_id=session_id,
            recipe_ids=recipe_ids,
        )
        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)
        return recommendation