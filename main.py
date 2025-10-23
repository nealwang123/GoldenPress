#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
水贝黄金价格实时监控系统
获取深圳水贝市场的实时黄金价格，支持定时监控和数据存储
"""

import argparse
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径，确保模块导入正常
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import GoldPriceScheduler, run_single_fetch, show_statistics
from data_storage import GoldPriceStorage
from gold_price_scraper import ShuiBeiGoldPriceScraper


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                  水贝黄金价格实时监控系统                    ║
    ║              ShuiBei Gold Price Monitoring System           ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_usage():
    """打印使用说明"""
    print("""
使用方法:
  python main.py [模式] [选项]

模式:
  single     单次获取当前水贝金价
  schedule   启动定时监控（每分钟获取一次）
  stats      显示历史数据统计
  test       测试数据源连接
  export     导出数据到Excel

选项:
  --interval MINUTES  定时模式下的间隔分钟数（默认: 1）
  --days DAYS         统计模式显示最近N天的数据（默认: 7）
  --file FILE         导出文件的路径

示例:
  python main.py single                    # 单次获取价格
  python main.py schedule                  # 启动定时监控
  python main.py schedule --interval 5     # 每5分钟获取一次
  python main.py stats                     # 显示统计信息
  python main.py stats --days 30           # 显示最近30天统计
  python main.py test                      # 测试数据源
  python main.py export                    # 导出数据到Excel
    """)


def test_data_sources():
    """测试所有数据源的连接情况"""
    print("🔧 测试数据源连接...")
    print("=" * 60)

    scraper = ShuiBeiGoldPriceScraper()

    for i, source in enumerate(scraper.data_sources, 1):
        print(f"\n{i}. 测试: {source['name']}")
        print(f"   网址: {source['url']}")
        print(f"   描述: {source['description']}")

        try:
            response = scraper.session.get(source['url'], timeout=10)
            if response.status_code == 200:
                print("   ✅ 连接成功")
            else:
                print(f"   ⚠️  连接异常 (状态码: {response.status_code})")
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")


def export_data(output_file=None):
    """导出数据到Excel"""
    storage = GoldPriceStorage()

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"水贝金价数据_{timestamp}.xlsx"

    try:
        storage.export_to_excel(output_file)
        print(f"✅ 数据已成功导出到: {output_file}")
    except Exception as e:
        print(f"❌ 导出失败: {e}")


def main():
    """主函数"""
    print_banner()

    parser = argparse.ArgumentParser(
        description='水贝黄金价格实时监控系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s single                    # 单次获取价格
  %(prog)s schedule                  # 启动定时监控
  %(prog)s schedule --interval 5     # 每5分钟获取一次
  %(prog)s stats                     # 显示统计信息
  %(prog)s stats --days 30           # 显示最近30天统计
  %(prog)s test                      # 测试数据源
  %(prog)s export                    # 导出数据到Excel
        """
    )

    parser.add_argument(
        'mode',
        choices=['single', 'schedule', 'stats', 'test', 'export', 'help', 'clear'],
        nargs='?',
        default='single',
        help='运行模式: single(单次), schedule(定时), stats(统计), test(测试), export(导出), help(帮助), clear(清除数据)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=1,
        help='定时模式下的间隔分钟数 (默认: 1分钟)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='统计模式显示最近N天的数据 (默认: 7天)'
    )

    parser.add_argument(
        '--file',
        help='导出文件的路径'
    )

    # 如果没有参数，显示使用说明
    if len(sys.argv) == 1:
        print_usage()
        return

    args = parser.parse_args()

    try:
        if args.mode == 'single':
            print("🔍 单次获取水贝金价...")
            run_single_fetch()

        elif args.mode == 'schedule':
            print(f"⏰ 启动定时监控，每 {args.interval} 分钟获取一次...")
            scheduler = GoldPriceScheduler(interval_minutes=args.interval)

            try:
                scheduler.start()
                # 保持主线程运行
                while scheduler.is_running:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止监控...")
                scheduler.stop()
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                scheduler.stop()

        elif args.mode == 'stats':
            print(f"📊 显示最近 {args.days} 天的统计信息...")
            show_statistics()

        elif args.mode == 'test':
            test_data_sources()

        elif args.mode == 'export':
            export_data(args.file)

        elif args.mode == 'help':
            print_usage()

        elif args.mode == 'clear':
            print("🗑️  正在清除所有历史数据...")
            storage = GoldPriceStorage()
            storage.clear_all_data()

    except KeyboardInterrupt:
        print("\n\n🛑 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        print("💡 请检查网络连接或数据源是否可用")


if __name__ == "__main__":
    main()
