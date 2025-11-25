# 招标信息爬虫系统

一个用于采集国内主流招标网站招标信息的自动化工具，支持按行业、关键词筛选，生成美观的HTML报告。

## 功能特点

- 🔍 **多站点采集**: 支持中国政府采购网、中国招标投标公共服务平台等多个招标网站
- 🏷️ **智能筛选**: 按行业（金融、医疗、运营商等）和关键词（维保、数据库、大数据等）精准筛选
- 📊 **美观报告**: 生成响应式HTML报告，支持搜索和分类浏览
- ⚙️ **灵活配置**: YAML配置文件，轻松调整目标网站、行业和关键词
- 🔄 **自动去重**: 基于招标编号和内容哈希自动去重
- 📝 **详细日志**: 完整的运行日志，便于问题排查

## 目录结构

```
bid-crawler/
├── docs/                    # 文档
│   ├── requirements.md      # 需求文档
│   └── development.md       # 开发文档
├── src/                     # 源代码
├── config/                  # 配置文件
├── reports/                 # 报告输出
├── logs/                    # 运行日志
├── tests/                   # 测试代码
├── requirements.txt         # Python依赖
├── run.sh                   # Linux运行脚本
├── run.bat                  # Windows运行脚本
└── README.md                # 本文件
```

## 快速开始

### 1. 环境准备

```bash
# 克隆/下载项目后，进入目录
cd bid-crawler

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置调整

复制并编辑配置文件：

```bash
cp config/config.example.yaml config/config.yaml
```

根据需要修改 `config/config.yaml`：
- 调整目标行业和关键词
- 启用/禁用特定网站
- 设置采集参数（时间范围、请求间隔等）

### 3. 运行爬虫

```bash
# Linux/Mac
./run.sh

# Windows
run.bat

# 或直接使用Python
python -m src.main
```

### 4. 查看报告

报告生成在 `reports/` 目录下，使用浏览器打开 `bid_report_YYYY-MM-DD.html`。

## 配置说明

### 添加新的关键词

编辑 `config/config.yaml`，在 `tech_keywords` 下添加：

```yaml
tech_keywords:
  database:
    - "新关键词"
```

### 添加新的目标行业

```yaml
industries:
  - name: "新行业"
    enabled: true
    keywords:
      - "行业关键词1"
      - "行业关键词2"
```

### 添加新的招标网站

```yaml
websites:
  - name: "新网站名称"
    url: "https://example.com"
    search_url: "https://example.com/search"
    enabled: true
    parser: "new_parser"  # 需要开发对应解析器
```

## 定时运行

### Linux (Crontab)

```bash
# 每天早上8点运行
crontab -e
0 8 * * * /path/to/bid-crawler/run.sh
```

### Windows (计划任务)

使用任务计划程序添加基本任务，执行 `run.bat`。

## 文档

- [需求文档](docs/requirements.md) - 详细功能需求说明
- [开发文档](docs/development.md) - 技术设计和扩展指南

## 注意事项

1. **合规使用**: 请遵守目标网站的使用条款和robots.txt规则
2. **请求频率**: 默认设置了2秒请求间隔，请勿过于频繁访问
3. **仅供参考**: 采集的信息仅供内部参考，不得用于商业用途

## 许可证

MIT License
