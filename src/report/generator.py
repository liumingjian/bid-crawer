"""
报告生成器

负责生成HTML格式的招标信息报告
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Template
from ..models.bid_info import BidInfo
from ..config.config_manager import ConfigManager
from ..utils.helpers import ensure_dir, get_date_filename


class ReportGenerator:
    """报告生成器类"""

    def __init__(self, config: ConfigManager):
        """
        初始化报告生成器

        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = logging.getLogger('bid_crawler.report')
        self.output_config = config.get_output_config()

        # 报告配置
        self.report_dir = self.output_config.get('report_dir', './reports')
        self.report_name = self.output_config.get('report_name', 'bid_report_{date}.html')
        self.data_dir = self.output_config.get('data_dir', './data')
        self.save_raw_data = self.output_config.get('save_raw_data', True)

        # 确保目录存在
        ensure_dir(self.report_dir)
        if self.save_raw_data:
            ensure_dir(self.data_dir)

        # 模板路径
        self.template_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            'report.html'
        )

    def generate(
        self,
        items: List[BidInfo],
        output_path: Optional[str] = None
    ) -> str:
        """
        生成HTML报告

        Args:
            items: 招标信息列表
            output_path: 输出路径，None则使用默认路径

        Returns:
            报告文件路径
        """
        if not items:
            self.logger.warning("没有数据，跳过报告生成")
            return ""

        self.logger.info(f"开始生成报告，共 {len(items)} 条数据")

        # 准备数据
        context = self._prepare_context(items)

        # 渲染模板
        html = self._render_template(context)

        # 确定输出路径
        if output_path is None:
            output_path = self._get_default_path()

        # 保存报告
        self._save_report(html, output_path)

        # 保存原始数据
        if self.save_raw_data:
            self._save_raw_data(items)

        self.logger.info(f"报告生成完成: {output_path}")
        return output_path

    def _prepare_context(self, items: List[BidInfo]) -> Dict[str, Any]:
        """
        准备模板上下文数据

        Args:
            items: 招标信息列表

        Returns:
            上下文字典
        """
        # 按行业分组
        by_industry = self._group_by_industry(items)

        # 按来源分组
        by_source = self._group_by_source(items)

        # 关键词统计
        keyword_stats = self._count_keywords(items)

        return {
            'generate_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(items),
            'by_industry': by_industry,
            'by_source': by_source,
            'keyword_stats': keyword_stats,
            'items': [item.to_dict() for item in items]
        }

    def _group_by_industry(self, items: List[BidInfo]) -> Dict[str, List[Dict]]:
        """按行业分组"""
        groups = {}
        for item in items:
            industry = item.industry or '其他'
            if industry not in groups:
                groups[industry] = []
            groups[industry].append(item.to_dict())
        return groups

    def _group_by_source(self, items: List[BidInfo]) -> Dict[str, int]:
        """按来源统计"""
        stats = {}
        for item in items:
            source = item.source or '未知'
            stats[source] = stats.get(source, 0) + 1
        return stats

    def _count_keywords(self, items: List[BidInfo]) -> Dict[str, int]:
        """统计关键词"""
        stats = {}
        for item in items:
            for keyword in item.matched_keywords:
                stats[keyword] = stats.get(keyword, 0) + 1
        # 按出现次数排序
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))

    def _render_template(self, context: Dict[str, Any]) -> str:
        """
        渲染模板

        Args:
            context: 上下文数据

        Returns:
            HTML字符串
        """
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_str = f.read()

            template = Template(template_str)
            html = template.render(**context)
            return html

        except FileNotFoundError:
            self.logger.error(f"模板文件不存在: {self.template_path}")
            # 使用简单的默认模板
            return self._get_fallback_template(context)
        except Exception as e:
            self.logger.error(f"渲染模板失败: {e}")
            return self._get_fallback_template(context)

    def _get_fallback_template(self, context: Dict[str, Any]) -> str:
        """获取备用模板"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>招标信息报告</title>
</head>
<body>
    <h1>招标信息报告</h1>
    <p>生成时间: {context['generate_time']}</p>
    <p>总数: {context['total_count']}</p>
    <hr>
    <ul>
"""
        for item in context['items']:
            html += f"<li><a href=\"{item['url']}\" target=\"_blank\">{item['title']}</a></li>\n"
        html += "</ul></body></html>"
        return html

    def _get_default_path(self) -> str:
        """获取默认输出路径"""
        filename = get_date_filename(self.report_name)
        return os.path.join(self.report_dir, filename)

    def _save_report(self, html: str, output_path: str) -> None:
        """保存报告文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.logger.info(f"报告已保存: {output_path}")
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            raise

    def _save_raw_data(self, items: List[BidInfo]) -> None:
        """保存原始数据为JSON"""
        try:
            filename = get_date_filename('bid_data_{date}.json')
            data_path = os.path.join(self.data_dir, filename)

            data = [item.to_dict() for item in items]

            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"原始数据已保存: {data_path}")
        except Exception as e:
            self.logger.error(f"保存原始数据失败: {e}")
