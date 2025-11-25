"""
数据筛选器

负责根据配置规则筛选和去重招标信息
"""

from typing import List, Set, Dict, Any
import logging
from datetime import datetime, timedelta
from ..models.bid_info import BidInfo
from ..config.config_manager import ConfigManager
from ..utils.helpers import is_date_in_range


class DataFilter:
    """数据筛选器类"""

    def __init__(self, config: ConfigManager):
        """
        初始化数据筛选器

        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = logging.getLogger('bid_crawler.filter')
        self._seen_hashes: Set[str] = set()

        # 获取筛选配置
        self.filter_config = config.get_filter_config()
        self.date_range = self.filter_config.get('date_range', 7)
        self.min_amount = self.filter_config.get('min_amount', 0)
        self.max_amount = self.filter_config.get('max_amount', 0)

    def filter(self, items: List[BidInfo]) -> List[BidInfo]:
        """
        执行筛选

        Args:
            items: 招标信息列表

        Returns:
            筛选后的招标信息列表
        """
        if not items:
            return []

        self.logger.info(f"开始筛选，原始数据: {len(items)} 条")

        result = []
        stats = {
            'total': len(items),
            'invalid': 0,
            'duplicate': 0,
            'no_keywords': 0,
            'out_of_date': 0,
            'out_of_amount': 0,
            'passed': 0
        }

        for item in items:
            # 验证数据有效性
            if not item.is_valid():
                stats['invalid'] += 1
                self.logger.debug(f"无效数据: {item.title[:50]}")
                continue

            # 去重检查
            if not self._check_duplicate(item):
                stats['duplicate'] += 1
                self.logger.debug(f"重复数据: {item.title[:50]}")
                continue

            # 关键词检查
            if not self._match_keywords(item):
                stats['no_keywords'] += 1
                self.logger.debug(f"不匹配关键词: {item.title[:50]}")
                continue

            # 日期检查
            if not self._check_date_range(item):
                stats['out_of_date'] += 1
                self.logger.debug(f"超出日期范围: {item.title[:50]}")
                continue

            # 金额检查
            if not self._check_amount_range(item):
                stats['out_of_amount'] += 1
                self.logger.debug(f"超出金额范围: {item.title[:50]}")
                continue

            # 行业分类
            self._classify_industry(item)

            stats['passed'] += 1
            result.append(item)

        self.logger.info(
            f"筛选完成: 总数={stats['total']}, "
            f"无效={stats['invalid']}, "
            f"重复={stats['duplicate']}, "
            f"无关键词={stats['no_keywords']}, "
            f"超期={stats['out_of_date']}, "
            f"金额不符={stats['out_of_amount']}, "
            f"通过={stats['passed']}"
        )

        return result

    def _check_duplicate(self, item: BidInfo) -> bool:
        """
        检查是否重复

        Args:
            item: 招标信息

        Returns:
            是否通过（True=不重复）
        """
        # 计算哈希
        hash_value = item.calculate_hash()

        if hash_value in self._seen_hashes:
            return False

        self._seen_hashes.add(hash_value)
        return True

    def _match_keywords(self, item: BidInfo) -> bool:
        """
        检查关键词匹配

        Args:
            item: 招标信息

        Returns:
            是否匹配关键词
        """
        keywords = self.config.get_keywords()
        if not keywords:
            # 如果没有配置关键词，全部通过
            return True

        # 使用BidInfo自带的匹配方法
        return item.match_keywords(keywords)

    def _check_date_range(self, item: BidInfo) -> bool:
        """
        检查日期范围

        Args:
            item: 招标信息

        Returns:
            是否在日期范围内
        """
        if self.date_range <= 0:
            # 不限制日期
            return True

        if not item.publish_date:
            # 没有发布日期，放行
            return True

        return is_date_in_range(item.publish_date, self.date_range)

    def _check_amount_range(self, item: BidInfo) -> bool:
        """
        检查金额范围

        Args:
            item: 招标信息

        Returns:
            是否在金额范围内
        """
        if not item.budget:
            # 没有金额信息，放行
            return True

        # 检查最小金额
        if self.min_amount > 0 and item.budget < self.min_amount:
            return False

        # 检查最大金额
        if self.max_amount > 0 and item.budget > self.max_amount:
            return False

        return True

    def _classify_industry(self, item: BidInfo) -> None:
        """
        自动分类行业

        Args:
            item: 招标信息
        """
        industries = self.config.get_industries()
        if not industries:
            return

        # 使用BidInfo自带的分类方法
        item.classify_industry(industries)

    def get_statistics(self, items: List[BidInfo]) -> Dict[str, Any]:
        """
        获取统计信息

        Args:
            items: 招标信息列表

        Returns:
            统计信息字典
        """
        stats = {
            'total': len(items),
            'by_source': {},
            'by_industry': {},
            'by_date': {},
            'keywords': {}
        }

        for item in items:
            # 按来源统计
            source = item.source or '未知'
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

            # 按行业统计
            industry = item.industry or '其他'
            stats['by_industry'][industry] = stats['by_industry'].get(industry, 0) + 1

            # 按日期统计
            if item.publish_date:
                date_str = item.publish_date.strftime('%Y-%m-%d')
                stats['by_date'][date_str] = stats['by_date'].get(date_str, 0) + 1

            # 关键词统计
            for keyword in item.matched_keywords:
                stats['keywords'][keyword] = stats['keywords'].get(keyword, 0) + 1

        return stats

    def reset(self) -> None:
        """重置筛选器状态（清空去重记录）"""
        self._seen_hashes.clear()
        self.logger.info("筛选器状态已重置")
