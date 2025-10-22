"""
获取真实黄金价格的实用解决方案
结合多个数据源，提供稳定的黄金价格获取功能
"""

import json
import logging
from datetime import datetime
from typing import Dict

class RealGoldPriceFetcher:
    """真实黄金价格获取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })

    def get_fallback_price(self) -> Dict:
        """获取备用价格（当所有数据源都失败时使用）"""
        # 基于当前市场情况的合理估算
        # 2025年10月黄金价格通常在900+元/克
        current_estimate = 920.0  # 当前市场合理估算

        return {
            'source': '市场估算数据',
            'price': current_estimate,
            'timestamp': datetime.now().isoformat(),
            'note': '基于当前市场情况的估算价格，实际价格请参考官方渠道',
            'warning': '此为估算数据，仅供参考'
        }

    def get_gold_price(self) -> Dict:
        """获取黄金价格 - 主要方法"""
        logging.info("开始获取真实黄金价格...")

        # 尝试银行数据源
        try:
            from bank_gold_price import get_bank_gold_data
            bank_data = get_bank_gold_data()
            if bank_data and bank_data.get('price'):
                logging.info("从银行数据源获取价格: %s元/克", bank_data['price'])
                return bank_data
        except Exception as e:
            logging.warning("银行数据源失败: %s", e)

        # 尝试API数据源
        try:
            from gold_api import get_real_gold_price as get_gold_price_from_api
            api_data = get_gold_price_from_api()
            if api_data and api_data.get('price'):
                logging.info("从API数据源获取价格: %s元/克", api_data['price'])
                return api_data
        except Exception as e:
            logging.warning("API数据源失败: %s", e)

        # 当所有数据源都不可用时，返回合理的估算价格
        logging.warning("所有真实数据源均失败，使用估算价格")
        return self.get_fallback_price()


# 主要接口函数
def get_real_gold_price():
    """获取真实黄金价格"""
    fetcher = RealGoldPriceFetcher()
    return fetcher.get_gold_price()


if __name__ == "__main__":
    # 测试真实价格获取
    logging.basicConfig(level=logging.INFO)

    price_data = get_real_gold_price()
    print("真实黄金价格获取结果:")
    print(json.dumps(price_data, ensure_ascii=False, indent=2))
