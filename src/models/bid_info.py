"""
招标信息数据模型

定义招标信息的数据结构和相关方法
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class BidInfo:
    """招标信息数据模型"""

    # 基本信息（必填）
    title: str                              # 招标标题
    url: str                                # 原文链接
    source: str                             # 来源网站

    # 招标详情（可选）
    bid_no: Optional[str] = None            # 招标编号
    purchaser: Optional[str] = None         # 采购单位
    agency: Optional[str] = None            # 代理机构
    publish_date: Optional[datetime] = None # 发布日期
    deadline: Optional[datetime] = None     # 截止日期
    budget: Optional[float] = None          # 预算金额(万元)
    contact: Optional[str] = None           # 联系方式
    address: Optional[str] = None           # 地址

    # 分类信息
    industry: Optional[str] = None          # 所属行业
    matched_keywords: List[str] = field(default_factory=list)  # 匹配的关键词

    # 元数据
    crawl_time: datetime = field(default_factory=datetime.now)  # 采集时间
    content_hash: Optional[str] = None      # 内容哈希(用于去重)

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            字典格式的招标信息
        """
        data = asdict(self)

        # 转换datetime为字符串
        if self.publish_date:
            data['publish_date'] = self.publish_date.strftime('%Y-%m-%d')
        if self.deadline:
            data['deadline'] = self.deadline.strftime('%Y-%m-%d')
        if self.crawl_time:
            data['crawl_time'] = self.crawl_time.strftime('%Y-%m-%d %H:%M:%S')

        return data

    def to_json(self) -> str:
        """
        转换为JSON字符串

        Returns:
            JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BidInfo':
        """
        从字典创建BidInfo对象

        Args:
            data: 字典数据

        Returns:
            BidInfo对象
        """
        # 转换日期字符串为datetime
        if 'publish_date' in data and isinstance(data['publish_date'], str):
            try:
                data['publish_date'] = datetime.strptime(data['publish_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                data['publish_date'] = None

        if 'deadline' in data and isinstance(data['deadline'], str):
            try:
                data['deadline'] = datetime.strptime(data['deadline'], '%Y-%m-%d')
            except (ValueError, TypeError):
                data['deadline'] = None

        if 'crawl_time' in data and isinstance(data['crawl_time'], str):
            try:
                data['crawl_time'] = datetime.strptime(data['crawl_time'], '%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                data['crawl_time'] = datetime.now()

        return cls(**data)

    def match_keywords(self, keywords: List[str]) -> bool:
        """
        检查标题是否匹配关键词

        Args:
            keywords: 关键词列表

        Returns:
            是否匹配
        """
        if not keywords:
            return False

        title_lower = self.title.lower()
        matched = []

        for keyword in keywords:
            if keyword.lower() in title_lower:
                matched.append(keyword)

        if matched:
            self.matched_keywords = matched
            return True

        return False

    def classify_industry(self, industries: List[Dict[str, Any]]) -> Optional[str]:
        """
        自动分类行业

        Args:
            industries: 行业配置列表，每项包含 name 和 keywords

        Returns:
            行业名称，未匹配返回None
        """
        if not industries:
            return None

        # 检查采购单位名称
        purchaser_lower = (self.purchaser or '').lower()

        for industry_config in industries:
            industry_name = industry_config.get('name', '')
            industry_keywords = industry_config.get('keywords', [])

            for keyword in industry_keywords:
                if keyword.lower() in purchaser_lower:
                    self.industry = industry_name
                    return industry_name

        return None

    def calculate_hash(self) -> str:
        """
        计算内容哈希值用于去重

        Returns:
            哈希值
        """
        import hashlib

        # 使用标题+发布日期+采购单位作为唯一标识
        unique_str = f"{self.title}"
        if self.publish_date:
            unique_str += f"_{self.publish_date.strftime('%Y%m%d')}"
        if self.purchaser:
            unique_str += f"_{self.purchaser}"

        hash_value = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
        self.content_hash = hash_value
        return hash_value

    def is_valid(self) -> bool:
        """
        检查招标信息是否有效

        Returns:
            是否有效
        """
        # 必须有标题、URL和来源
        if not self.title or not self.url or not self.source:
            return False

        # 标题长度应该合理
        if len(self.title) < 5 or len(self.title) > 500:
            return False

        return True

    def __str__(self) -> str:
        """字符串表示"""
        return f"BidInfo(title='{self.title[:50]}...', source='{self.source}')"

    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"BidInfo(title='{self.title}', url='{self.url}', "
            f"source='{self.source}', purchaser='{self.purchaser}', "
            f"industry='{self.industry}')"
        )
