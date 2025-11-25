"""
中国采购与招标网解析器

解析 https://www.chinabidding.cn 的招标信息
"""

from typing import List, Dict, Any
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
import re
from ..base_parser import BaseParser
from ...utils.helpers import parse_date, parse_amount, clean_text


class ChinaBiddingParser(BaseParser):
    """中国采购与招标网解析器"""

    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """构造搜索URL"""
        keyword_str = " ".join(keywords) if keywords else ""

        params = {
            'keyword': keyword_str,
            'page': str(page),
            'categoryId': '',  # 分类ID，可配置
        }

        return f"{self.search_url}?{urlencode(params)}"

    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """解析列表页"""
        results = []

        try:
            soup = BeautifulSoup(html, 'lxml')

            # 查找列表项
            list_items = soup.select('.search-list-box li') or \
                        soup.select('.list_bid li') or \
                        soup.select('.table-box tr')

            for item in list_items:
                try:
                    # 提取标题和链接
                    title_elem = item.find('a')
                    if not title_elem:
                        continue

                    title = clean_text(title_elem.get_text())
                    url = title_elem.get('href', '')

                    if not title or not url:
                        continue

                    # 补全URL
                    if not url.startswith('http'):
                        url = urljoin(self.url, url)

                    # 提取发布日期
                    publish_date = None
                    date_elem = item.find('span', class_='time') or \
                               item.find('td', class_='time')

                    if date_elem:
                        date_text = clean_text(date_elem.get_text())
                        publish_date = parse_date(date_text)
                    else:
                        # 从文本中提取日期
                        text = item.get_text()
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                        if date_match:
                            publish_date = parse_date(date_match.group(1))

                    # 提取地区/单位信息
                    purchaser = None
                    area_elem = item.find('span', class_='area') or \
                               item.find('td', class_='area')
                    if area_elem:
                        purchaser = clean_text(area_elem.get_text())

                    results.append({
                        'title': title,
                        'url': url,
                        'publish_date': publish_date,
                        'purchaser': purchaser,
                    })

                except Exception as e:
                    self.logger.warning(f"解析列表项失败: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"解析列表页失败: {e}")

        return results
