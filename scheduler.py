import schedule
import time
import threading
from datetime import datetime
from typing import Callable, Optional
import logging

from gold_price_scraper import ShuiBeiGoldPriceScraper
from data_storage import GoldPriceStorage

class GoldPriceScheduler:
    """黄金价格定时调度器"""
    
    def __init__(self, interval_minutes: int = 1):
        self.interval_minutes = interval_minutes
        self.scraper = ShuiBeiGoldPriceScraper()
        self.storage = GoldPriceStorage()
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
    
    def fetch_and_store_price(self):
        """获取并存储黄金价格"""
        try:
            self.logger.info(f"开始获取水贝金价... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 获取价格数据
            price_data = self.scraper.get_gold_price()
            
            # 存储数据
            self.storage.save_price_data(price_data)
            
            # 打印当前价格信息
            if price_data.get('price'):
                print(f"🟢 [{datetime.now().strftime('%H:%M:%S')}] 水贝金价: {price_data['price']}元/克 (来源: {price_data['source']})")
            else:
                print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] 获取失败: {price_data.get('error', '未知错误')}")
                
        except Exception as e:
            self.logger.error(f"获取和存储金价时发生错误: {e}")
            print(f"🔴 [{datetime.now().strftime('%H:%M:%S')}] 错误: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每分钟执行一次
        schedule.every(self.interval_minutes).minutes.do(self.fetch_and_store_price)
        
        # 立即执行一次
        self.fetch_and_store_price()
        
        self.logger.info(f"定时任务已设置，每 {self.interval_minutes} 分钟执行一次")
        print(f"⏰ 定时任务已启动，每 {self.interval_minutes} 分钟获取一次水贝金价")
    
    def run_scheduler(self):
        """运行调度器"""
        self.is_running = True
        self.setup_schedule()
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)  # 每秒检查一次是否有待执行的任务
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，停止调度器")
            print("\n🛑 收到中断信号，停止调度器...")
        except Exception as e:
            self.logger.error(f"调度器运行错误: {e}")
            print(f"❌ 调度器错误: {e}")
        finally:
            self.is_running = False
    
    def start(self):
        """启动调度器（在新线程中）"""
        if self.is_running:
            self.logger.warning("调度器已经在运行")
            print("⚠️ 调度器已经在运行")
            return
        
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("调度器线程已启动")
        print("🚀 调度器已启动，按 Ctrl+C 停止")
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        self.logger.info("调度器已停止")
        print("🛑 调度器已停止")
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'interval_minutes': self.interval_minutes,
            'next_run': str(schedule.next_run()) if schedule.jobs else None,
            'pending_jobs': len(schedule.jobs)
        }


def run_single_fetch():
    """单次获取价格（用于测试）"""
    scraper = ShuiBeiGoldPriceScraper()
    storage = GoldPriceStorage()
    
    print("🔍 正在获取水贝金价...")
    price_data = scraper.get_gold_price()
    
    if price_data.get('price'):
        print(f"💰 当前水贝金价: {price_data['price']}元/克")
        print(f"📊 数据来源: {price_data['source']}")
        print(f"⏰ 更新时间: {price_data['timestamp']}")
        
        # 保存数据
        storage.save_price_data(price_data)
        
        # 显示统计信息
        stats = storage.get_price_statistics()
        if 'current_price' in stats:
            print(f"📈 统计信息: 当前{stats['current_price']}元/克, 最低{stats['min_price']}元/克, 最高{stats['max_price']}元/克")
    else:
        print(f"❌ 获取失败: {price_data.get('error', '未知错误')}")


def show_statistics():
    """显示统计信息"""
    storage = GoldPriceStorage()
    stats = storage.get_price_statistics()
    
    print("\n📊 水贝金价统计信息")
    print("=" * 50)
    
    if 'error' in stats:
        print(f"❌ 错误: {stats['error']}")
        return
    
    if stats.get('valid_price_records', 0) == 0:
        print("📝 暂无有效价格数据")
        return
    
    print(f"📈 当前价格: {stats['current_price']} 元/克")
    print(f"📉 最低价格: {stats['min_price']} 元/克")
    print(f"📈 最高价格: {stats['max_price']} 元/克")
    print(f"📊 平均价格: {stats['avg_price']:.2f} 元/克")
    print(f"📋 价格标准差: {stats['price_std']:.2f} 元/克")
    print(f"📝 总记录数: {stats['total_records']}")
    print(f"✅ 有效价格记录: {stats['valid_price_records']}")
    print(f"🕒 最后更新: {stats['latest_update']}")
    
    if stats.get('data_sources'):
        print("\n📡 数据来源分布:")
        for source, count in stats['data_sources'].items():
            print(f"  - {source}: {count} 次")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='水贝金价监控工具')
    parser.add_argument('--mode', choices=['single', 'schedule', 'stats'], 
                       default='single', help='运行模式: single(单次), schedule(定时), stats(统计)')
    parser.add_argument('--interval', type=int, default=1, 
                       help='定时模式下的间隔分钟数 (默认: 1分钟)')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        run_single_fetch()
    elif args.mode == 'stats':
        show_statistics()
    elif args.mode == 'schedule':
        scheduler = GoldPriceScheduler(interval_minutes=args.interval)
        
        try:
            scheduler.start()
            # 保持主线程运行
            while scheduler.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止调度器...")
            scheduler.stop()
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            scheduler.stop()
