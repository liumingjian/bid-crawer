"""
爬虫引擎

负责调度各网站解析器，执行采集任务
"""

from typing import List, Dict, Any, Optional
import logging
from ..config.config_manager import ConfigManager
from ..models.bid_info import BidInfo
from ..utils.http_client import HttpClient
from .base_parser import BaseParser
from .parsers.ccgp_parser import CCGPParser
from .parsers.cebp_parser import CEBPParser
from .parsers.chinabidding_parser import ChinaBiddingParser


class CrawlerEngine:
    """爬虫引擎类"""

    def __init__(self, config: ConfigManager):
        """
        初始化爬虫引擎

        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = logging.getLogger('bid_crawler.engine')
        self.parsers: Dict[str, BaseParser] = {}

        # 创建HTTP客户端
        crawler_config = config.get_crawler_config()
        self.http_client = HttpClient(crawler_config)

        # 注册所有解析器
        self._register_parsers()

    def _register_parsers(self) -> None:
        """注册所有可用的解析器"""
        # 解析器映射表
        parser_classes = {
            'ccgp': CCGPParser,
            'cebp': CEBPParser,
            'chinabidding': ChinaBiddingParser,
        }

        websites = self.config.get_websites()
        self.logger.info(f"开始注册解析器，共 {len(websites)} 个网站")

        for website in websites:
            parser_name = website.get('parser', '')
            website_name = website.get('name', '')

            if not parser_name:
                self.logger.warning(f"网站 '{website_name}' 未配置解析器")
                continue

            if parser_name not in parser_classes:
                self.logger.warning(f"未找到解析器: {parser_name}")
                continue

            try:
                parser_class = parser_classes[parser_name]
                parser = parser_class(website, self.http_client)
                self.parsers[parser_name] = parser
                self.logger.info(f"注册解析器成功: {parser_name} -> {website_name}")
            except Exception as e:
                self.logger.error(f"注册解析器失败 {parser_name}: {e}")

    def get_parser(self, parser_name: str) -> Optional[BaseParser]:
        """
        获取指定解析器

        Args:
            parser_name: 解析器名称

        Returns:
            解析器实例，未找到返回None
        """
        return self.parsers.get(parser_name)

    def crawl_website(
        self,
        website: Dict[str, Any],
        keywords: List[str],
        max_pages: Optional[int] = None
    ) -> List[BidInfo]:
        """
        采集单个网站的数据

        Args:
            website: 网站配置字典
            keywords: 关键词列表
            max_pages: 最大页数，None则使用配置值

        Returns:
            BidInfo对象列表
        """
        parser_name = website.get('parser', '')
        website_name = website.get('name', '')

        parser = self.get_parser(parser_name)
        if not parser:
            self.logger.error(f"未找到解析器: {parser_name}")
            return []

        # 确定最大页数
        if max_pages is None:
            max_pages = self.config.get('crawler.max_pages', 10)

        self.logger.info(f"开始采集网站: {website_name}, 最大页数: {max_pages}")

        try:
            items = parser.fetch_all(keywords, max_pages)
            self.logger.info(f"{website_name} 采集完成，共 {len(items)} 条数据")
            return items

        except Exception as e:
            self.logger.error(f"采集网站失败 {website_name}: {e}")
            return []

    def crawl_all(self, max_pages: Optional[int] = None) -> List[BidInfo]:
        """
        采集所有启用网站的数据

        Args:
            max_pages: 最大页数，None则使用配置值

        Returns:
            BidInfo对象列表
        """
        all_items = []
        websites = self.config.get_websites()
        keywords = self.config.get_keywords()

        if not websites:
            self.logger.warning("没有启用的网站")
            return []

        if not keywords:
            self.logger.warning("没有配置关键词")
            return []

        self.logger.info(f"开始采集，共 {len(websites)} 个网站，{len(keywords)} 个关键词")

        for website in websites:
            try:
                items = self.crawl_website(website, keywords, max_pages)
                all_items.extend(items)
                self.logger.info(f"当前总计: {len(all_items)} 条数据")

            except Exception as e:
                website_name = website.get('name', '')
                self.logger.error(f"采集网站异常 {website_name}: {e}")
                # 继续采集其他网站
                continue

        self.logger.info(f"所有网站采集完成，总计 {len(all_items)} 条数据")
        return all_items

    def close(self) -> None:
        """关闭HTTP客户端"""
        if self.http_client:
            self.http_client.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
