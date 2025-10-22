"""
模拟水贝黄金价格数据源
当真实数据源不可用时，使用模拟数据演示程序功能
"""

import random
from datetime import datetime
import json

class MockGoldPriceSource:
    """模拟黄金价格数据源"""
    
    def __init__(self):
        # 模拟基础价格范围（元/克）
        self.base_price_range = (480.0, 520.0)
        self.current_price = 500.0
        self.price_history = []
    
    def generate_mock_price(self):
        """生成模拟价格数据"""
        # 模拟价格波动（±2元）
        price_change = random.uniform(-2.0, 2.0)
        self.current_price += price_change
        
        # 确保价格在合理范围内
        self.current_price = max(self.base_price_range[0], 
                               min(self.base_price_range[1], self.current_price))
        
        price_data = {
            'source': '模拟数据源-水贝金价',
            'price': round(self.current_price, 2),
            'timestamp': datetime.now().isoformat(),
            'raw_text': f'水贝黄金价格 {self.current_price:.2f}元/克',
            'note': '此为模拟数据，仅供参考'
        }
        
        self.price_history.append(price_data)
        return price_data
    
    def get_mock_statistics(self, days=7):
        """生成模拟统计信息"""
        if len(self.price_history) == 0:
            return {
                'total_records': 0,
                'valid_price_records': 0,
                'message': '暂无模拟数据'
            }
        
        prices = [data['price'] for data in self.price_history]
        
        return {
            'total_records': len(self.price_history),
            'valid_price_records': len(self.price_history),
            'current_price': prices[-1],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': round(sum(prices) / len(prices), 2),
            'price_std': round((sum((p - sum(prices)/len(prices))**2 for p in prices) / len(prices))**0.5, 2),
            'data_sources': {'模拟数据源-水贝金价': len(self.price_history)},
            'latest_update': self.price_history[-1]['timestamp']
        }


# 全局模拟数据源实例
mock_source = MockGoldPriceSource()


def get_mock_gold_price():
    """获取模拟黄金价格"""
    return mock_source.generate_mock_price()


def get_mock_statistics(days=7):
    """获取模拟统计信息"""
    return mock_source.get_mock_statistics(days)


if __name__ == "__main__":
    # 测试模拟数据
    print("🔧 测试模拟数据源...")
    for i in range(5):
        price_data = get_mock_gold_price()
        print(f"模拟价格 {i+1}: {price_data['price']}元/克")
    
    stats = get_mock_statistics()
    print("\n📊 模拟统计信息:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
