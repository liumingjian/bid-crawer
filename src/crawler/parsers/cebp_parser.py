"""
中国招标投标公共服务平台解析器

解析 http://www.cebpubservice.com 的招标信息
"""

from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
from ..base_parser import BaseParser
from ...utils.helpers import parse_date, parse_amount, clean_text


class CEBPParser(BaseParser):
    """中国招标投标公共服务平台解析器"""

    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """构造列表页URL"""
        # 该网站可能需要POST请求或有特殊的分页方式
        # 这里提供基本实现
        if page == 1:
            return self.search_url
        else:
            # 分页URL格式: index_{page}.html
            base = self.search_url.rsplit('/', 1)[0]
            return f"{base}/index_{page}.html"

    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """解析列表页"""
        results = []

        try:
            soup = BeautifulSoup(html, 'lxml')

            # 查找列表项
            list_items = soup.select('ul.xxgg_con_list li') or \
                        soup.select('.news_list li') or \
                        soup.select('.list-item')

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
                    date_text = item.get_text()
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                    if date_match:
                        publish_date = parse_date(date_match.group(1))

                    results.append({
                        'title': title,
                        'url': url,
                        'publish_date': publish_date,
                    })

                except Exception as e:
                    self.logger.warning(f"解析列表项失败: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"解析列表页失败: {e}")

        return results
