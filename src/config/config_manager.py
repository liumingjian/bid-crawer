"""
配置管理器

负责加载、验证、访问配置信息
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from .settings import DEFAULT_CONFIG


class ConfigManager:
    """配置管理器类"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # 合并默认配置
            self.config = self._merge_defaults(self.config, DEFAULT_CONFIG)

            # 验证配置
            if not self.validate():
                raise ValueError("配置文件验证失败")

        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")

    def _merge_defaults(self, config: Dict, defaults: Dict) -> Dict:
        """
        合并默认配置

        Args:
            config: 用户配置
            defaults: 默认配置

        Returns:
            合并后的配置
        """
        result = defaults.copy()

        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_defaults(value, result[key])
            else:
                result[key] = value

        return result

    def validate(self) -> bool:
        """
        验证配置有效性

        Returns:
            配置是否有效
        """
        try:
            # 检查必要的顶级键
            required_keys = ['crawler', 'filters', 'output', 'logging']
            for key in required_keys:
                if key not in self.config:
                    print(f"警告: 配置中缺少 '{key}' 部分")
                    return False

            # 检查网站配置
            if 'websites' not in self.config or not self.config['websites']:
                print("警告: 配置中缺少网站列表")
                return False

            # 检查关键词配置
            if 'tech_keywords' not in self.config or not self.config['tech_keywords']:
                print("警告: 配置中缺少技术关键词")

            return True

        except Exception as e:
            print(f"配置验证错误: {e}")
            return False

    def reload(self) -> None:
        """重新加载配置（支持热更新）"""
        self._load()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'crawler.timeout'
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_websites(self) -> List[Dict[str, Any]]:
        """
        获取启用的网站列表

        Returns:
            网站配置列表
        """
        websites = self.config.get('websites', [])
        return [site for site in websites if site.get('enabled', False)]

    def get_keywords(self) -> List[str]:
        """
        获取所有关键词（扁平化）

        Returns:
            关键词列表
        """
        keywords = []
        tech_keywords = self.config.get('tech_keywords', {})

        # 从技术关键词中提取
        if isinstance(tech_keywords, dict):
            for category, kws in tech_keywords.items():
                if isinstance(kws, list):
                    keywords.extend(kws)
        elif isinstance(tech_keywords, list):
            keywords.extend(tech_keywords)

        return keywords

    def get_industries(self) -> List[Dict[str, Any]]:
        """
        获取启用的行业配置

        Returns:
            行业配置列表
        """
        industries = self.config.get('industries', [])
        return [ind for ind in industries if ind.get('enabled', True)]

    def get_crawler_config(self) -> Dict[str, Any]:
        """获取爬虫配置"""
        return self.config.get('crawler', {})

    def get_filter_config(self) -> Dict[str, Any]:
        """获取筛选配置"""
        return self.config.get('filters', {})

    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.config.get('output', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get('logging', {})
