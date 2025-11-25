"""
中国政府采购网解析器

解析 https://www.ccgp.gov.cn 的招标信息
"""

from typing import List, Dict, Any
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
import re
from ..base_parser import BaseParser
from ...utils.helpers import parse_date, parse_amount, clean_text


class CCGPParser(BaseParser):
    """中国政府采购网解析器"""

    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """
        构造搜索URL

        中国政府采购网搜索接口格式:
        https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={page}&...
        """
        # 组合关键词（空格分隔）
        keyword_str = " ".join(keywords) if keywords else ""

        params = {
            'searchtype': '1',  # 1=招标公告, 2=中标公告
            'page_index': str(page),
            'bidSort': '0',
            'pinMu': '0',
            'bidType': '1',
            'kw': keyword_str,
            'start_time': '',  # 开始时间，可根据需求配置
            'end_time': '',    # 结束时间
            'timeType': '6',   # 时间类型，6=发布时间
        }

        return f"{self.search_url}?{urlencode(params)}"

    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """解析列表页"""
        results = []

        try:
            soup = BeautifulSoup(html, 'lxml')

            # 查找列表项（根据实际网站结构调整选择器）
            # 政府采购网的结构可能是 <ul class="vT-srch-result-list-bid">
            list_items = soup.select('ul.vT-srch-result-list-bid li') or \
                        soup.select('ul.c_list_bid li') or \
                        soup.select('.list_16 li')

            if not list_items:
                self.logger.warning("未找到列表项，尝试其他选择器")
                # 尝试更通用的选择器
                list_items = soup.find_all('li', class_=re.compile(r'(list|item|result)'))

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
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = urljoin(self.url, url)
                    elif not url.startswith('http'):
                        url = urljoin(self.search_url, url)

                    # 提取发布日期
                    publish_date = None
                    date_elem = item.find('span', class_='time') or \
                               item.find('span', class_='date') or \
                               item.find('span', text=re.compile(r'\d{4}-\d{2}-\d{2}'))

                    if date_elem:
                        date_text = clean_text(date_elem.get_text())
                        publish_date = parse_date(date_text)

                    # 提取采购单位
                    purchaser = None
                    purchaser_elem = item.find('span', text=re.compile(r'(采购人|招标人|业主)')) or \
                                    item.find('span', class_='purchaser')

                    if purchaser_elem:
                        purchaser_text = clean_text(purchaser_elem.get_text())
                        # 移除前缀
                        purchaser = re.sub(r'^(采购人|招标人|业主)[：:]\s*', '', purchaser_text)
                    else:
                        # 尝试从标题或其他位置提取
                        text = item.get_text()
                        match = re.search(r'(采购人|招标人|业主)[：:]\s*([^\s\|]+)', text)
                        if match:
                            purchaser = match.group(2).strip()

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

    def parse_detail(self, url: str) -> Dict[str, Any]:
        """
        解析详情页（可选实现）

        提取更详细的招标信息
        """
        try:
            html = self.http_client.get(url)
            soup = BeautifulSoup(html, 'lxml')

            detail = {}

            # 提取招标编号
            bid_no_elem = soup.find(text=re.compile(r'(项目编号|招标编号)'))
            if bid_no_elem:
                parent = bid_no_elem.find_parent()
                if parent:
                    bid_no_text = parent.get_text()
                    match = re.search(r'[：:]\s*([A-Z0-9\-]+)', bid_no_text)
                    if match:
                        detail['bid_no'] = match.group(1).strip()

            # 提取预算金额
            budget_elem = soup.find(text=re.compile(r'(预算金额|采购预算|项目金额)'))
            if budget_elem:
                parent = budget_elem.find_parent()
                if parent:
                    budget_text = parent.get_text()
                    budget = parse_amount(budget_text)
                    if budget:
                        detail['budget'] = budget

            # 提取截止日期
            deadline_elem = soup.find(text=re.compile(r'(截止时间|投标截止|报名截止)'))
            if deadline_elem:
                parent = deadline_elem.find_parent()
                if parent:
                    deadline_text = parent.get_text()
                    deadline = parse_date(deadline_text)
                    if deadline:
                        detail['deadline'] = deadline

            # 提取代理机构
            agency_elem = soup.find(text=re.compile(r'(代理机构|招标代理)'))
            if agency_elem:
                parent = agency_elem.find_parent()
                if parent:
                    agency_text = parent.get_text()
                    match = re.search(r'[：:]\s*([^：\n\r]+)', agency_text)
                    if match:
                        detail['agency'] = match.group(1).strip()

            return detail

        except Exception as e:
            self.logger.error(f"解析详情页失败 {url}: {e}")
            return {}
