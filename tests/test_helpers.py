"""
辅助函数模块单元测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.helpers import parse_date, parse_amount, clean_text, calculate_hash
from datetime import datetime


def test_parse_date():
    """测试日期解析"""
    # 测试标准格式
    assert parse_date("2024-01-15") == datetime(2024, 1, 15)
    assert parse_date("2024/01/15") == datetime(2024, 1, 15)
    assert parse_date("2024年01月15日") == datetime(2024, 1, 15)

    # 测试无效输入
    assert parse_date("") is None
    assert parse_date("invalid") is None

    print("✓ test_parse_date passed")


def test_parse_amount():
    """测试金额解析"""
    # 测试不同单位
    assert parse_amount("100万元") == 100.0
    assert parse_amount("1.5亿元") == 15000.0
    assert parse_amount("50000元") == 5.0

    # 测试无效输入
    assert parse_amount("") is None
    assert parse_amount("invalid") is None

    print("✓ test_parse_amount passed")


def test_clean_text():
    """测试文本清理"""
    assert clean_text("  hello   world  ") == "hello world"
    assert clean_text("hello\n\nworld") == "hello world"
    assert clean_text("") == ""

    print("✓ test_clean_text passed")


def test_calculate_hash():
    """测试哈希计算"""
    text1 = "hello world"
    text2 = "hello world"
    text3 = "different"

    assert calculate_hash(text1) == calculate_hash(text2)
    assert calculate_hash(text1) != calculate_hash(text3)

    print("✓ test_calculate_hash passed")


if __name__ == '__main__':
    print("Running tests...")
    print("=" * 50)

    test_parse_date()
    test_parse_amount()
    test_clean_text()
    test_calculate_hash()

    print("=" * 50)
    print("All tests passed! ✓")
