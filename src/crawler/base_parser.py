"""
解析器基类

所有网站解析器必须继承此类并实现抽象方法
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from ..models.bid_info import BidInfo
from ..utils.http_client import HttpClient


class BaseParser(ABC):
    """网站解析器基类"""

    def __init__(self, config: Dict[str, Any], http_client: HttpClient):
        """
        初始化解析器

        Args:
            config: 网站配置字典
            http_client: HTTP客户端实例
        """
        self.config = config
        self.http_client = http_client
        self.logger = logging.getLogger(f'bid_crawler.parser.{self.get_name()}')

        # 网站配置
        self.name = config.get('name', '')
        self.url = config.get('url', '')
        self.search_url = config.get('search_url', '')
        self.encoding = config.get('encoding', 'utf-8')

    @abstractmethod
    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """
        构造列表页URL

        Args:
            page: 页码（从1开始）
            keywords: 关键词列表

        Returns:
            列表页URL
        """
        pass

    @abstractmethod
    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """
        解析列表页，返回招标信息基本数据

        Args:
            html: HTML内容

        Returns:
            招标信息字典列表，每项应包含:
            - title: 标题
            - url: 详情链接
            - publish_date: 发布日期（可选）
            - purchaser: 采购单位（可选）
            - source: 来源网站
        """
        pass

    def parse_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """
        解析详情页，返回完整招标信息（可选实现）

        Args:
            url: 详情页URL

        Returns:
            详细信息字典，可包含:
            - bid_no: 招标编号
            - budget: 预算金额
            - deadline: 截止日期
            - contact: 联系方式
            - agency: 代理机构
            等其他信息
        """
        # 默认不解析详情页
        return None

    def fetch_list(
        self,
        page: int,
        keywords: List[str],
        max_retries: int = 3
    ) -> List[BidInfo]:
        """
        获取列表页数据

        Args:
            page: 页码
            keywords: 关键词列表
            max_retries: 最大重试次数

        Returns:
            BidInfo对象列表
        """
        try:
            url = self.get_list_url(page, keywords)
            self.logger.info(f"正在获取第 {page} 页: {url}")

            html = self.http_client.get(url)
            if not html:
                self.logger.warning(f"获取页面失败: {url}")
                return []

            items = self.parse_list(html)
            self.logger.info(f"解析到 {len(items)} 条数据")

            # 转换为BidInfo对象
            bid_infos = []
            for item in items:
                try:
                    # 确保必填字段存在
                    if not item.get('title') or not item.get('url'):
                        continue

                    # 设置来源
                    item['source'] = self.name

                    bid_info = BidInfo(**item)
                    bid_infos.append(bid_info)
                except Exception as e:
                    self.logger.warning(f"创建BidInfo失败: {e}, 数据: {item}")
                    continue

            return bid_infos

        except Exception as e:
            self.logger.error(f"获取列表页失败: {e}")
            return []

    def fetch_all(
        self,
        keywords: List[str],
        max_pages: int = 10
    ) -> List[BidInfo]:
        """
        获取所有页面数据

        Args:
            keywords: 关键词列表
            max_pages: 最大页数

        Returns:
            BidInfo对象列表
        """
        all_items = []

        for page in range(1, max_pages + 1):
            try:
                items = self.fetch_list(page, keywords)

                if not items:
                    self.logger.info(f"第 {page} 页无数据，停止采集")
                    break

                all_items.extend(items)
                self.logger.info(f"已采集 {len(all_items)} 条数据")

            except Exception as e:
                self.logger.error(f"采集第 {page} 页时出错: {e}")
                # 继续采集下一页
                continue

        return all_items

    def get_name(self) -> str:
        """获取解析器名称"""
        return self.__class__.__name__

    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.get_name()}(name='{self.name}')"
