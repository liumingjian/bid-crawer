# 招标信息爬虫系统 - 开发文档

## 1. 系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        主控制器 (main.py)                        │
│                    负责调度、流程控制、异常处理                     │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  配置管理器    │      │   爬虫引擎     │      │  报告生成器    │
│ ConfigManager │      │ CrawlerEngine │      │ ReportGenerator│
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│  config.yaml  │      │  网站解析器    │      │  HTML模板     │
│               │      │   Parsers     │      │  templates/   │
└───────────────┘      └───────────────┘      └───────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌───────────┐   ┌───────────┐   ┌───────────┐
        │  CCGP     │   │  CEBP     │   │  其他...   │
        │  Parser   │   │  Parser   │   │  Parser   │
        └───────────┘   └───────────┘   └───────────┘
```

### 1.2 目录结构

```
bid-crawler/
├── docs/                       # 文档目录
│   ├── requirements.md         # 需求文档
│   └── development.md          # 开发文档
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── main.py                 # 主入口
│   ├── config/                 # 配置模块
│   │   ├── __init__.py
│   │   ├── config_manager.py   # 配置管理器
│   │   └── settings.py         # 默认设置
│   ├── crawler/                # 爬虫模块
│   │   ├── __init__.py
│   │   ├── engine.py           # 爬虫引擎
│   │   ├── base_parser.py      # 解析器基类
│   │   └── parsers/            # 各网站解析器
│   │       ├── __init__.py
│   │       ├── ccgp_parser.py  # 中国政府采购网
│   │       ├── cebp_parser.py  # 中国招标投标公共服务平台
│   │       └── ...
│   ├── filter/                 # 数据筛选模块
│   │   ├── __init__.py
│   │   └── data_filter.py      # 数据筛选器
│   ├── report/                 # 报告生成模块
│   │   ├── __init__.py
│   │   ├── generator.py        # 报告生成器
│   │   └── templates/          # HTML模板
│   │       └── report.html     # 报告模板
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   └── bid_info.py         # 招标信息模型
│   └── utils/                  # 工具模块
│       ├── __init__.py
│       ├── logger.py           # 日志工具
│       ├── http_client.py      # HTTP客户端
│       └── helpers.py          # 辅助函数
├── config/                     # 配置文件目录
│   ├── config.yaml             # 主配置文件
│   └── config.example.yaml     # 配置示例
├── reports/                    # 报告输出目录
├── logs/                       # 日志目录
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_crawler.py
│   └── test_filter.py
├── requirements.txt            # 依赖列表
├── setup.py                    # 安装脚本
├── run.sh                      # Linux运行脚本
├── run.bat                     # Windows运行脚本
└── README.md                   # 项目说明
```

## 2. 模块设计

### 2.1 配置管理模块 (config/)

#### 2.1.1 ConfigManager 类

```python
class ConfigManager:
    """配置管理器
    
    负责加载、验证、访问配置信息
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化配置管理器"""
        pass
    
    def load(self) -> dict:
        """加载配置文件"""
        pass
    
    def validate(self) -> bool:
        """验证配置有效性"""
        pass
    
    def get_websites(self) -> List[WebsiteConfig]:
        """获取启用的网站列表"""
        pass
    
    def get_keywords(self) -> List[str]:
        """获取所有关键词"""
        pass
    
    def get_industries(self) -> List[IndustryConfig]:
        """获取行业配置"""
        pass
    
    def reload(self) -> None:
        """重新加载配置（支持热更新）"""
        pass
```

#### 2.1.2 配置文件格式 (config.yaml)

```yaml
# ============================================
# 招标信息爬虫系统配置文件
# ============================================

# 爬虫基础配置
crawler:
  request_delay: 2              # 请求间隔(秒)，避免频繁请求
  timeout: 30                   # 请求超时时间(秒)
  retry_times: 3                # 失败重试次数
  retry_delay: 5                # 重试间隔(秒)
  max_pages: 10                 # 每个网站最大采集页数
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 数据筛选配置
filters:
  date_range: 7                 # 采集最近N天的数据
  min_amount: 0                 # 最小预算金额(万元)，0表示不限
  max_amount: 0                 # 最大预算金额(万元)，0表示不限
  title_must_contain: []        # 标题必须包含的词（AND关系）
  title_any_contain: []         # 标题包含任意词即可（OR关系）

# 目标行业配置
industries:
  - name: "金融"
    enabled: true
    keywords:
      - "银行"
      - "证券"
      - "保险"
      - "基金"
      - "信托"
      - "金融"
  
  - name: "医疗"
    enabled: true
    keywords:
      - "医院"
      - "卫健委"
      - "卫生健康"
      - "疾控中心"
      - "医疗"
      - "中医院"
  
  - name: "运营商"
    enabled: true
    keywords:
      - "移动"
      - "联通"
      - "电信"
      - "广电"
      - "通信"
  
  - name: "政府"
    enabled: true
    keywords:
      - "政务"
      - "大数据局"
      - "数据资源"
      - "政府"
      - "机关"
  
  - name: "能源"
    enabled: true
    keywords:
      - "电力"
      - "电网"
      - "石油"
      - "石化"
      - "燃气"
      - "能源"
  
  - name: "教育"
    enabled: true
    keywords:
      - "大学"
      - "学院"
      - "高校"
      - "教育"

# 技术关键词配置
tech_keywords:
  # 运维服务类
  service:
    - "维保"
    - "运维"
    - "技术支持"
    - "驻场"
    - "运营服务"
    - "技术服务"
  
  # 数据库类
  database:
    - "数据库"
    - "GaussDB"
    - "高斯数据库"
    - "OceanBase"
    - "TiDB"
    - "达梦"
    - "人大金仓"
    - "MySQL"
    - "Oracle"
    - "PostgreSQL"
    - "SQL Server"
  
  # 大数据类
  bigdata:
    - "大数据"
    - "Hadoop"
    - "CDH"
    - "Cloudera"
    - "Spark"
    - "Hive"
    - "HBase"
    - "Kafka"
    - "Flink"
    - "ClickHouse"
    - "Doris"
    - "数据仓库"
    - "数据湖"
    - "数据中台"
  
  # 中间件类
  middleware:
    - "中间件"
    - "Redis"
    - "RabbitMQ"
    - "Nginx"
    - "Tomcat"
    - "WebLogic"
    - "消息队列"
    - "缓存"
  
  # 信创类
  xinchuang:
    - "信创"
    - "国产化"
    - "自主可控"
    - "国产数据库"
    - "国产中间件"

# 目标网站配置
websites:
  - name: "中国政府采购网"
    url: "https://www.ccgp.gov.cn"
    search_url: "https://search.ccgp.gov.cn/bxsearch"
    enabled: true
    parser: "ccgp"
    encoding: "utf-8"
    notes: "政府采购主站，数据量大"
  
  - name: "中国招标投标公共服务平台"
    url: "http://www.cebpubservice.com"
    search_url: "http://www.cebpubservice.com/xxgg/index.html"
    enabled: true
    parser: "cebp"
    encoding: "utf-8"
    notes: "综合招标平台"
  
  - name: "中国采购与招标网"
    url: "https://www.chinabidding.cn"
    search_url: "https://www.chinabidding.cn/search/searchzbgg"
    enabled: true
    parser: "chinabidding"
    encoding: "utf-8"
    notes: "综合招标信息"
  
  - name: "全国公共资源交易平台"
    url: "http://www.ggzy.gov.cn"
    search_url: "http://www.ggzy.gov.cn/information/html/a/index.html"
    enabled: false
    parser: "ggzy"
    encoding: "utf-8"
    notes: "公共资源交易，结构复杂"
  
  - name: "比地招标网"
    url: "https://www.bidizhaobiao.com"
    search_url: "https://www.bidizhaobiao.com/zbgg"
    enabled: false
    parser: "bidi"
    encoding: "utf-8"
    notes: "第三方招标聚合平台"

# 输出配置
output:
  report_dir: "./reports"                    # 报告输出目录
  report_name: "bid_report_{date}.html"      # 报告文件名模板
  data_dir: "./data"                         # 原始数据保存目录
  save_raw_data: true                        # 是否保存原始数据(JSON)
  keep_days: 30                              # 报告保留天数

# 日志配置
logging:
  level: "INFO"                              # 日志级别: DEBUG, INFO, WARNING, ERROR
  file: "./logs/crawler.log"                 # 日志文件路径
  max_size: 10                               # 单个日志文件最大MB
  backup_count: 5                            # 保留日志文件数量
```

### 2.2 爬虫引擎模块 (crawler/)

#### 2.2.1 CrawlerEngine 类

```python
class CrawlerEngine:
    """爬虫引擎
    
    负责调度各网站解析器，执行采集任务
    """
    
    def __init__(self, config: ConfigManager):
        """初始化爬虫引擎"""
        self.config = config
        self.parsers = {}
        self.http_client = HttpClient()
        self._register_parsers()
    
    def _register_parsers(self) -> None:
        """注册所有可用的解析器"""
        pass
    
    def crawl_all(self) -> List[BidInfo]:
        """采集所有启用网站的数据"""
        pass
    
    def crawl_website(self, website: WebsiteConfig) -> List[BidInfo]:
        """采集单个网站的数据"""
        pass
    
    def get_parser(self, parser_name: str) -> BaseParser:
        """获取指定解析器"""
        pass
```

#### 2.2.2 BaseParser 基类

```python
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """网站解析器基类
    
    所有网站解析器必须继承此类并实现抽象方法
    """
    
    def __init__(self, config: WebsiteConfig, http_client: HttpClient):
        self.config = config
        self.http_client = http_client
    
    @abstractmethod
    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """构造列表页URL"""
        pass
    
    @abstractmethod
    def parse_list(self, html: str) -> List[dict]:
        """解析列表页，返回招标信息基本数据"""
        pass
    
    @abstractmethod
    def parse_detail(self, url: str) -> dict:
        """解析详情页，返回完整招标信息"""
        pass
    
    def fetch_list(self, page: int, keywords: List[str]) -> List[BidInfo]:
        """获取列表页数据"""
        url = self.get_list_url(page, keywords)
        html = self.http_client.get(url)
        items = self.parse_list(html)
        return [BidInfo(**item) for item in items]
```

#### 2.2.3 解析器实现示例 (CCGP)

```python
class CCGPParser(BaseParser):
    """中国政府采购网解析器"""
    
    def get_list_url(self, page: int, keywords: List[str]) -> str:
        """构造搜索URL
        
        中国政府采购网搜索接口格式:
        https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={page}&...
        """
        base_url = "https://search.ccgp.gov.cn/bxsearch"
        params = {
            "searchtype": "1",
            "page_index": page,
            "bidSort": "0",
            "pinMu": "0",
            "bidType": "1",  # 1=招标公告
            "kw": "+".join(keywords)
        }
        return f"{base_url}?{urlencode(params)}"
    
    def parse_list(self, html: str) -> List[dict]:
        """解析列表页"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for item in soup.select('.vT-srch-result-list li'):
            title_elem = item.select_one('a')
            if not title_elem:
                continue
            
            results.append({
                'title': title_elem.get_text(strip=True),
                'url': title_elem.get('href'),
                'publish_date': self._extract_date(item),
                'purchaser': self._extract_purchaser(item),
                'source': '中国政府采购网'
            })
        
        return results
    
    def parse_detail(self, url: str) -> dict:
        """解析详情页"""
        html = self.http_client.get(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取详细信息
        return {
            'bid_no': self._extract_bid_no(soup),
            'budget': self._extract_budget(soup),
            'deadline': self._extract_deadline(soup),
            'content': self._extract_content(soup)
        }
```

### 2.3 数据模型 (models/)

#### 2.3.1 BidInfo 模型

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class BidInfo:
    """招标信息数据模型"""
    
    # 基本信息
    title: str                              # 招标标题
    url: str                                # 原文链接
    source: str                             # 来源网站
    
    # 招标详情
    bid_no: Optional[str] = None            # 招标编号
    purchaser: Optional[str] = None         # 采购单位
    agency: Optional[str] = None            # 代理机构
    publish_date: Optional[datetime] = None # 发布日期
    deadline: Optional[datetime] = None     # 截止日期
    budget: Optional[float] = None          # 预算金额(万元)
    
    # 分类信息
    industry: Optional[str] = None          # 所属行业
    matched_keywords: List[str] = field(default_factory=list)  # 匹配的关键词
    
    # 元数据
    crawl_time: datetime = field(default_factory=datetime.now) # 采集时间
    content_hash: Optional[str] = None      # 内容哈希(用于去重)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        pass
    
    def match_keywords(self, keywords: List[str]) -> bool:
        """检查是否匹配关键词"""
        pass
    
    def classify_industry(self, industries: List[IndustryConfig]) -> str:
        """自动分类行业"""
        pass
```

### 2.4 数据筛选模块 (filter/)

#### 2.4.1 DataFilter 类

```python
class DataFilter:
    """数据筛选器
    
    负责根据配置规则筛选和去重招标信息
    """
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self._seen_hashes = set()
    
    def filter(self, items: List[BidInfo]) -> List[BidInfo]:
        """执行筛选"""
        result = []
        for item in items:
            if self._should_include(item):
                result.append(item)
        return result
    
    def _should_include(self, item: BidInfo) -> bool:
        """判断是否应包含该项"""
        # 去重检查
        if not self._check_duplicate(item):
            return False
        
        # 关键词检查
        if not self._match_keywords(item):
            return False
        
        # 日期检查
        if not self._check_date_range(item):
            return False
        
        # 金额检查
        if not self._check_amount_range(item):
            return False
        
        return True
    
    def _check_duplicate(self, item: BidInfo) -> bool:
        """检查是否重复"""
        hash_value = item.content_hash or hash(f"{item.title}{item.publish_date}")
        if hash_value in self._seen_hashes:
            return False
        self._seen_hashes.add(hash_value)
        return True
    
    def _match_keywords(self, item: BidInfo) -> bool:
        """检查关键词匹配"""
        keywords = self.config.get_keywords()
        title_lower = item.title.lower()
        
        matched = []
        for kw in keywords:
            if kw.lower() in title_lower:
                matched.append(kw)
        
        item.matched_keywords = matched
        return len(matched) > 0
```

### 2.5 报告生成模块 (report/)

#### 2.5.1 ReportGenerator 类

```python
class ReportGenerator:
    """报告生成器
    
    负责生成HTML格式的招标信息报告
    """
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.template_path = "src/report/templates/report.html"
    
    def generate(self, items: List[BidInfo], output_path: str = None) -> str:
        """生成HTML报告"""
        # 准备数据
        context = self._prepare_context(items)
        
        # 渲染模板
        html = self._render_template(context)
        
        # 保存文件
        if output_path is None:
            output_path = self._get_default_path()
        
        self._save_report(html, output_path)
        return output_path
    
    def _prepare_context(self, items: List[BidInfo]) -> dict:
        """准备模板上下文数据"""
        return {
            'generate_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(items),
            'by_industry': self._group_by_industry(items),
            'by_source': self._group_by_source(items),
            'items': [item.to_dict() for item in items]
        }
    
    def _group_by_industry(self, items: List[BidInfo]) -> dict:
        """按行业分组"""
        groups = {}
        for item in items:
            industry = item.industry or '其他'
            if industry not in groups:
                groups[industry] = []
            groups[industry].append(item)
        return groups
```

#### 2.5.2 HTML模板设计

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>招标信息报告 - {{ generate_time }}</title>
    <style>
        /* 响应式设计样式 */
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .bid-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .bid-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .bid-title a {
            color: #3498db;
            text-decoration: none;
        }
        .bid-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            font-size: 14px;
            color: #666;
        }
        .keyword-tag {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .industry-tag {
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .filter-bar {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .filter-bar input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            .header { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>招标信息报告</h1>
        <p>生成时间: {{ generate_time }}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>{{ total_count }}</h3>
            <p>招标总数</p>
        </div>
        {% for source, items in by_source.items() %}
        <div class="stat-card">
            <h3>{{ items|length }}</h3>
            <p>{{ source }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="filter-bar">
        <input type="text" id="searchInput" placeholder="搜索招标标题或单位..." onkeyup="filterItems()">
    </div>
    
    <div id="bidList">
        {% for item in items %}
        <div class="bid-card" data-title="{{ item.title }}" data-purchaser="{{ item.purchaser }}">
            <div class="bid-title">
                <a href="{{ item.url }}" target="_blank">{{ item.title }}</a>
            </div>
            <div class="bid-meta">
                <span>📅 {{ item.publish_date }}</span>
                <span>🏢 {{ item.purchaser }}</span>
                {% if item.budget %}
                <span>💰 {{ item.budget }}万元</span>
                {% endif %}
                <span class="industry-tag">{{ item.industry }}</span>
                {% for kw in item.matched_keywords %}
                <span class="keyword-tag">{{ kw }}</span>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <script>
        function filterItems() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.bid-card');
            cards.forEach(card => {
                const title = card.dataset.title.toLowerCase();
                const purchaser = card.dataset.purchaser.toLowerCase();
                if (title.includes(input) || purchaser.includes(input)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
```

### 2.6 工具模块 (utils/)

#### 2.6.1 HttpClient 类

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HttpClient:
    """HTTP客户端
    
    封装requests，提供重试、代理、限速等功能
    """
    
    def __init__(self, config: dict = None):
        self.session = requests.Session()
        self._setup_retry()
        self._setup_headers(config)
        self.delay = config.get('request_delay', 2) if config else 2
    
    def _setup_retry(self):
        """配置重试策略"""
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def get(self, url: str, params: dict = None, **kwargs) -> str:
        """发送GET请求"""
        time.sleep(self.delay)  # 限速
        response = self.session.get(url, params=params, **kwargs)
        response.raise_for_status()
        return response.text
    
    def post(self, url: str, data: dict = None, **kwargs) -> str:
        """发送POST请求"""
        time.sleep(self.delay)
        response = self.session.post(url, data=data, **kwargs)
        response.raise_for_status()
        return response.text
```

#### 2.6.2 Logger 配置

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(config: dict) -> logging.Logger:
    """配置日志"""
    logger = logging.getLogger('bid_crawler')
    logger.setLevel(config.get('level', 'INFO'))
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        config.get('file', 'logs/crawler.log'),
        maxBytes=config.get('max_size', 10) * 1024 * 1024,
        backupCount=config.get('backup_count', 5),
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## 3. 技术选型

### 3.1 核心依赖

| 库名 | 版本 | 用途 |
|------|------|------|
| requests | >=2.28.0 | HTTP请求 |
| beautifulsoup4 | >=4.11.0 | HTML解析 |
| lxml | >=4.9.0 | HTML/XML解析加速 |
| PyYAML | >=6.0 | 配置文件解析 |
| Jinja2 | >=3.1.0 | HTML模板渲染 |
| python-dateutil | >=2.8.0 | 日期处理 |
| fake-useragent | >=1.1.0 | User-Agent生成 |

### 3.2 可选依赖

| 库名 | 用途 |
|------|------|
| selenium | 处理JavaScript渲染页面 |
| playwright | 现代化浏览器自动化 |
| schedule | 定时任务 |
| pandas | 数据处理和导出Excel |

## 4. 部署方案

### 4.1 虚拟环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 4.2 运行脚本

**Linux/Mac (run.sh):**
```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python -m src.main "$@"
```

**Windows (run.bat):**
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python -m src.main %*
```

### 4.3 定时任务配置

**Linux Crontab:**
```bash
# 每天早上8点执行
0 8 * * * /path/to/bid-crawler/run.sh >> /path/to/bid-crawler/logs/cron.log 2>&1
```

**Windows 计划任务:**
使用任务计划程序创建基本任务，执行 run.bat

## 5. 扩展指南

### 5.1 新增网站解析器

1. 在 `src/crawler/parsers/` 下创建新文件，如 `new_site_parser.py`
2. 继承 `BaseParser` 类并实现抽象方法
3. 在 `config.yaml` 中添加网站配置
4. 在 `CrawlerEngine._register_parsers()` 中注册新解析器

```python
# src/crawler/parsers/new_site_parser.py
from ..base_parser import BaseParser

class NewSiteParser(BaseParser):
    """新网站解析器"""
    
    def get_list_url(self, page: int, keywords: List[str]) -> str:
        # 实现URL构造逻辑
        pass
    
    def parse_list(self, html: str) -> List[dict]:
        # 实现列表页解析逻辑
        pass
    
    def parse_detail(self, url: str) -> dict:
        # 实现详情页解析逻辑
        pass
```

### 5.2 添加新的关键词类别

在 `config.yaml` 的 `tech_keywords` 下添加新类别：

```yaml
tech_keywords:
  # 新类别
  new_category:
    - "关键词1"
    - "关键词2"
```

### 5.3 自定义报告模板

1. 复制 `src/report/templates/report.html` 为新模板
2. 修改模板内容和样式
3. 在配置中指定使用新模板

## 6. 测试计划

### 6.1 单元测试

- ConfigManager: 配置加载、验证、热更新
- DataFilter: 关键词匹配、日期筛选、去重逻辑
- BidInfo: 数据转换、分类逻辑
- 各Parser: URL构造、HTML解析

### 6.2 集成测试

- 完整采集流程测试
- 报告生成测试
- 定时任务测试

### 6.3 测试数据

- 准备模拟HTML文件用于解析测试
- 准备配置文件测试用例

## 7. 注意事项

### 7.1 反爬策略应对

- 设置合理的请求间隔（2-5秒）
- 随机化User-Agent
- 支持代理IP切换（预留接口）
- 处理验证码页面（记录日志，跳过）

### 7.2 数据质量保证

- 严格的数据清洗和校验
- 完善的异常处理和日志记录
- 支持断点续采

### 7.3 维护建议

- 定期检查网站结构变化
- 及时更新解析规则
- 定期清理旧报告和日志
