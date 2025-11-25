"""
默认配置设置

提供系统默认配置值，当配置文件缺少某些字段时使用这些默认值
"""

DEFAULT_CONFIG = {
    'crawler': {
        'request_delay': 2,
        'timeout': 30,
        'retry_times': 3,
        'retry_delay': 5,
        'max_pages': 10,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    },
    'filters': {
        'date_range': 7,
        'min_amount': 0,
        'max_amount': 0,
        'title_must_contain': [],
        'title_any_contain': []
    },
    'output': {
        'report_dir': './reports',
        'report_name': 'bid_report_{date}.html',
        'data_dir': './data',
        'save_raw_data': True,
        'keep_days': 30
    },
    'logging': {
        'level': 'INFO',
        'file': './logs/crawler.log',
        'max_size': 10,
        'backup_count': 5
    }
}
