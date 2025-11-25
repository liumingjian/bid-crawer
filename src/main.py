"""
招标信息爬虫系统 - 主入口程序

整合所有模块，执行完整的采集、筛选、报告生成流程
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager
from src.crawler.engine import CrawlerEngine
from src.filter.data_filter import DataFilter
from src.report.generator import ReportGenerator
from src.utils.logger import setup_logger


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='招标信息爬虫系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src.main                    # 使用默认配置运行
  python -m src.main --config custom.yaml  # 使用自定义配置
  python -m src.main --max-pages 5      # 限制每个网站最多采集5页
        """
    )

    parser.add_argument(
        '-c', '--config',
        default='config/config.yaml',
        help='配置文件路径 (默认: config/config.yaml)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        help='每个网站最大采集页数 (覆盖配置文件)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析参数
    args = parse_args()

    # 加载配置
    try:
        config = ConfigManager(args.config)
    except Exception as e:
        print(f"错误: 加载配置文件失败: {e}")
        return 1

    # 设置日志
    log_config = config.get_logging_config()
    if args.verbose:
        log_config['level'] = 'DEBUG'
    logger = setup_logger('bid_crawler', log_config)

    logger.info("=" * 60)
    logger.info("招标信息爬虫系统启动")
    logger.info("=" * 60)

    try:
        # 1. 创建爬虫引擎
        logger.info("初始化爬虫引擎...")
        with CrawlerEngine(config) as engine:

            # 2. 采集数据
            logger.info("开始采集招标信息...")
            raw_items = engine.crawl_all(max_pages=args.max_pages)

            if not raw_items:
                logger.warning("未采集到任何数据")
                return 0

            logger.info(f"采集完成，共 {len(raw_items)} 条原始数据")

            # 3. 筛选数据
            logger.info("开始筛选数据...")
            data_filter = DataFilter(config)
            filtered_items = data_filter.filter(raw_items)

            if not filtered_items:
                logger.warning("筛选后无数据")
                return 0

            logger.info(f"筛选完成，保留 {len(filtered_items)} 条数据")

            # 打印统计信息
            stats = data_filter.get_statistics(filtered_items)
            logger.info("数据统计:")
            logger.info(f"  - 总数: {stats['total']}")
            logger.info(f"  - 按来源: {stats['by_source']}")
            logger.info(f"  - 按行业: {stats['by_industry']}")

            # 4. 生成报告
            logger.info("开始生成报告...")
            report_gen = ReportGenerator(config)
            report_path = report_gen.generate(filtered_items)

            logger.info("=" * 60)
            logger.info(f"✓ 任务完成！")
            logger.info(f"✓ 报告已生成: {report_path}")
            logger.info("=" * 60)

            return 0

    except KeyboardInterrupt:
        logger.warning("\n用户中断执行")
        return 130
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
