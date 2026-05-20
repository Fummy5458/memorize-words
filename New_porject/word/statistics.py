# word/statistics.py
# 【新增】背诵统计与正确率模块
import json
import os
import time

STATS_FILE = os.path.join(os.path.dirname(__file__), "study_stats.json")

def get_today_date():
    """获取今天日期：YYYY-MM-DD"""
    return time.strftime("%Y-%m-%d")

def init_stats():
    """初始化统计数据"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 默认结构
    return {
        "total_studied": 0,        # 累计学习单词数
        "total_correct": 0,        # 累计正确数
        "daily": {},               # 每日记录
        "last_file": None          # 最后学习的词库
    }

def record_study(correct):
    """记录一次学习：correct=True/False"""
    stats = init_stats()
    today = get_today_date()

    # 全局统计
    stats["total_studied"] += 1
    if correct:
        stats["total_correct"] += 1

    # 今日统计
    if today not in stats["daily"]:
        stats["daily"][today] = {"studied": 0, "correct": 0}
    stats["daily"][today]["studied"] += 1
    if correct:
        stats["daily"][today]["correct"] += 1

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def get_accuracy():
    """获取总正确率"""
    s = init_stats()
    if s["total_studied"] == 0:
        return 0.0
    return round(s["total_correct"] / s["total_studied"] * 100, 1)

def get_today_progress():
    """获取今日学习数、正确数、正确率"""
    s = init_stats()
    today = get_today_date()
    data = s["daily"].get(today, {"studied": 0, "correct": 0})
    acc = 0.0
    if data["studied"] > 0:
        acc = round(data["correct"] / data["studied"] * 100, 1)
    return data["studied"], data["correct"], acc