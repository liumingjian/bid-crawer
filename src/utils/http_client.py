"""
HTTP客户端

封装requests，提供重试、代理、限速等功能
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
import logging


class HttpClient:
    """HTTP客户端类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化HTTP客户端

        Args:
            config: 爬虫配置字典，包含:
                - request_delay: 请求间隔(秒)
                - timeout: 超时时间(秒)
                - retry_times: 重试次数
                - user_agent: User-Agent字符串
        """
        self.config = config or {}
        self.session = requests.Session()
        self.logger = logging.getLogger('bid_crawler.http')

        # 配置参数
        self.delay = self.config.get('request_delay', 2)
        self.timeout = self.config.get('timeout', 30)
        self.retry_times = self.config.get('retry_times', 3)
        self.user_agent = self.config.get(
            'user_agent',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 设置重试策略
        self._setup_retry()

        # 设置默认headers
        self._setup_headers()

        # 记录最后一次请求时间
        self._last_request_time = 0

    def _setup_retry(self) -> None:
        """配置重试策略"""
        retry_strategy = Retry(
            total=self.retry_times,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _setup_headers(self) -> None:
        """设置默认请求头"""
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def _rate_limit(self) -> None:
        """请求限速"""
        if self.delay > 0:
            elapsed = time.time() - self._last_request_time
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                time.sleep(sleep_time)
        self._last_request_time = time.time()

    def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """
        发送GET请求

        Args:
            url: 请求URL
            params: URL参数
            headers: 额外的请求头
            **kwargs: 其他requests参数

        Returns:
            响应文本

        Raises:
            requests.RequestException: 请求失败
        """
        self._rate_limit()

        try:
            self.logger.debug(f"GET {url}")

            if headers:
                kwargs['headers'] = {**self.session.headers, **headers}

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()

            # 尝试检测编码
            if response.encoding == 'ISO-8859-1':
                # 尝试从content中检测编码
                encodings = ['utf-8', 'gbk', 'gb2312']
                for encoding in encodings:
                    try:
                        response.encoding = encoding
                        _ = response.text
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue

            return response.text

        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {url}, 错误: {e}")
            raise

    def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """
        发送POST请求

        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 额外的请求头
            **kwargs: 其他requests参数

        Returns:
            响应文本

        Raises:
            requests.RequestException: 请求失败
        """
        self._rate_limit()

        try:
            self.logger.debug(f"POST {url}")

            if headers:
                kwargs['headers'] = {**self.session.headers, **headers}

            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()

            return response.text

        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {url}, 错误: {e}")
            raise

    def close(self) -> None:
        """关闭会话"""
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
