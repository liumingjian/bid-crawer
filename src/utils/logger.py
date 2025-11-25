"""
日志工具模块

提供统一的日志记录功能
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from pathlib import Path


def setup_logger(
    name: str = 'bid_crawler',
    config: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    配置并返回日志记录器

    Args:
        name: 日志记录器名称
        config: 日志配置字典，包含以下键:
            - level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            - file: 日志文件路径
            - max_size: 单个日志文件最大MB
            - backup_count: 保留日志文件数量

    Returns:
        配置好的日志记录器
    """
    # 使用默认配置
    if config is None:
        config = {
            'level': 'INFO',
            'file': './logs/crawler.log',
            'max_size': 10,
            'backup_count': 5
        }

    # 创建日志记录器
    logger = logging.getLogger(name)

    # 如果logger已经有handlers，说明已经配置过了，直接返回
    if logger.handlers:
        return logger

    # 设置日志级别
    level_str = config.get('level', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # 创建日志目录
    log_file = config.get('file', './logs/crawler.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 创建文件处理器（带日志轮转）
    max_bytes = config.get('max_size', 10) * 1024 * 1024  # 转换为字节
    backup_count = config.get('backup_count', 5)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 创建格式化器
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # 设置格式化器
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = 'bid_crawler') -> logging.Logger:
    """
    获取已配置的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)
