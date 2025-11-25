"""
辅助函数模块

提供各种通用的辅助函数
"""

import re
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
import os


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析日期字符串

    Args:
        date_str: 日期字符串

    Returns:
        datetime对象，解析失败返回None
    """
    if not date_str:
        return None

    # 移除多余空白字符
    date_str = date_str.strip()

    # 常见日期格式
    date_patterns = [
        r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})',  # 2024-01-15, 2024/01/15, 2024年01月15日
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',  # 2024.01.15
        r'(\d{4})(\d{2})(\d{2})',  # 20240115
    ]

    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                year, month, day = map(int, match.groups())
                return datetime(year, month, day)
            except ValueError:
                continue

    return None


def parse_amount(amount_str: str) -> Optional[float]:
    """
    解析金额字符串，统一转换为万元

    Args:
        amount_str: 金额字符串，如 "100万元", "1.5亿元", "500元"

    Returns:
        金额（万元），解析失败返回None
    """
    if not amount_str:
        return None

    # 移除多余字符
    amount_str = re.sub(r'[,，\s]', '', amount_str)

    # 提取数字
    match = re.search(r'([\d.]+)', amount_str)
    if not match:
        return None

    try:
        value = float(match.group(1))
    except ValueError:
        return None

    # 判断单位
    if '亿' in amount_str:
        value *= 10000  # 亿转换为万
    elif '万' in amount_str:
        pass  # 已经是万
    elif '千' in amount_str:
        value /= 10  # 千转换为万
    elif '元' in amount_str and '万' not in amount_str and '亿' not in amount_str:
        value /= 10000  # 元转换为万
    else:
        # 如果没有单位，假设是万元
        pass

    return round(value, 2)


def calculate_hash(text: str) -> str:
    """
    计算文本的MD5哈希值

    Args:
        text: 输入文本

    Returns:
        MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def is_date_in_range(date: datetime, days: int) -> bool:
    """
    检查日期是否在最近N天内

    Args:
        date: 要检查的日期
        days: 天数

    Returns:
        是否在范围内
    """
    if not date:
        return False

    now = datetime.now()
    date_limit = now - timedelta(days=days)
    return date >= date_limit


def clean_text(text: str) -> str:
    """
    清理文本，移除多余空白字符

    Args:
        text: 输入文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除多余空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除首尾空白
    text = text.strip()

    return text


def extract_keywords_from_text(text: str, keyword_list: List[str]) -> List[str]:
    """
    从文本中提取匹配的关键词

    Args:
        text: 文本内容
        keyword_list: 关键词列表

    Returns:
        匹配的关键词列表
    """
    if not text or not keyword_list:
        return []

    text_lower = text.lower()
    matched = []

    for keyword in keyword_list:
        if keyword.lower() in text_lower:
            matched.append(keyword)

    return matched


def ensure_dir(directory: str) -> None:
    """
    确保目录存在，不存在则创建

    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_date_filename(template: str, date: Optional[datetime] = None) -> str:
    """
    根据模板生成带日期的文件名

    Args:
        template: 文件名模板，如 "report_{date}.html"
        date: 日期对象，默认为当前日期

    Returns:
        文件名
    """
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%Y%m%d')
    return template.replace('{date}', date_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断文本

    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length] + suffix
