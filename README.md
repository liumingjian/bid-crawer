# 招标信息爬虫系统

一个自动化采集国内主流招标网站招标信息的Python爬虫系统，支持关键词筛选、行业分类、数据去重，并生成美观的HTML报告。

## 📋 功能特性

- ✅ **多网站采集**：支持中国政府采购网、中国招标投标公共服务平台、中国采购与招标网等
- 🎯 **智能筛选**：基于关键词、行业、日期、金额等多维度筛选
- 🏷️ **行业分类**：自动识别金融、医疗、运营商、政府、能源、教育等行业
- 🔍 **关键词匹配**：支持数据库、大数据、中间件、信创等技术关键词
- 🚫 **自动去重**：基于内容哈希自动去除重复数据
- 📊 **可视化报告**：生成响应式HTML报告，支持搜索和筛选
- ⚙️ **灵活配置**：通过YAML配置文件轻松管理
- 📝 **详细日志**：完整的日志记录，便于调试和监控

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Linux / macOS / Windows

### 安装步骤

1. **克隆项目**

\`\`\`bash
git clone <repository-url>
cd bid-crawer
\`\`\`

2. **运行系统**

Linux/Mac:
\`\`\`bash
./run.sh
\`\`\`

Windows:
\`\`\`bash
run.bat
\`\`\`

首次运行会自动创建虚拟环境并安装依赖包。

### 配置文件

编辑 \`config/config.yaml\` 进行自定义配置：

\`\`\`yaml
# 爬虫配置
crawler:
  request_delay: 2        # 请求间隔(秒)
  max_pages: 10          # 每个网站最大采集页数

# 筛选配置
filters:
  date_range: 7          # 采集最近N天的数据
  min_amount: 0          # 最小金额(万元)

# 技术关键词
tech_keywords:
  database:
    - "数据库"
    - "GaussDB"
    - "MySQL"
  bigdata:
    - "大数据"
    - "Hadoop"
    - "Spark"
\`\`\`

## 📖 使用说明

### 基本用法

\`\`\`bash
# 使用默认配置运行
python -m src.main

# 使用自定义配置
python -m src.main --config custom.yaml

# 限制采集页数
python -m src.main --max-pages 5

# 显示详细日志
python -m src.main --verbose
\`\`\`

### 输出文件

- **HTML报告**: \`reports/bid_report_YYYYMMDD.html\`
- **原始数据**: \`data/bid_data_YYYYMMDD.json\`
- **日志文件**: \`logs/crawler.log\`

## 🏗️ 项目结构

\`\`\`
bid-crawer/
├── src/                      # 源代码目录
│   ├── config/              # 配置管理模块
│   ├── crawler/             # 爬虫核心模块
│   │   └── parsers/         # 各网站解析器
│   ├── filter/              # 数据筛选模块
│   ├── report/              # 报告生成模块
│   ├── models/              # 数据模型
│   ├── utils/               # 工具模块
│   └── main.py              # 主入口程序
├── config/                   # 配置文件目录
├── reports/                  # 报告输出目录
├── data/                     # 原始数据目录
├── logs/                     # 日志目录
├── requirements.txt          # 依赖列表
├── run.sh                    # Linux/Mac运行脚本
└── README.md                 # 本文档
\`\`\`

## 🔧 扩展开发

### 添加新网站解析器

1. 在 \`src/crawler/parsers/\` 目录下创建新的解析器文件
2. 继承 \`BaseParser\` 类并实现抽象方法
3. 在 \`config.yaml\` 中添加网站配置
4. 在 \`CrawlerEngine\` 中注册新解析器

## ⚠️ 注意事项

1. **遵守法律法规**：采集的信息仅供内部参考使用
2. **尊重网站规则**：遵守目标网站的robots.txt规则
3. **控制请求频率**：避免对目标网站造成过大压力
4. **数据变化**：网站结构可能变化，需要定期维护解析器

## 📝 开发文档

详细的技术文档请查看：

- [需求文档](requirements.md)
- [开发文档](development.md)

---

**注意**：本项目采集的是公开招标信息，请合理使用，遵守相关法律法规。
