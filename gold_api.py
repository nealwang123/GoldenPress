"""
使用金融API获取真实黄金价格数据
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Optional

class GoldPriceAPI:
    """黄金价格API类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })

        # 公开的黄金价格API
        self.api_endpoints = [
            {
                'name': 'Alpha Vantage黄金价格',
                'url': 'https://www.alphavantage.co/query',
                'params': {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': 'GC=F',
                    'apikey': 'demo'  # 免费API密钥，有调用限制
                },
                'parser': self._parse_alpha_vantage
            },
            {
                'name': '金属价格API',
                'url': 'https://api.metalpriceapi.com/v1/latest',
                'params': {
                    'api_key': 'demo',  # 需要注册获取真实API密钥
                    'base': 'XAU',
                    'currencies': 'CNY'
                },
                'parser': self._parse_metalpriceapi
            }
        ]

    def _parse_alpha_vantage(self, data: dict) -> Optional[Dict]:
        """解析Alpha Vantage API返回的数据"""
        try:
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                price_usd = float(quote.get('05. price', 0))
                # 简单汇率转换（实际应该使用实时汇率）
                price_cny = price_usd * 7.2  # 近似汇率
                return {
                    'price': round(price_cny / 31.1035, 2),  # 转换为元/克
                    'raw_data': quote
                }
        except Exception as e:
            logging.error(f"解析Alpha Vantage数据失败: {e}")
        return None

    def _parse_metalpriceapi(self, data: dict) -> Optional[Dict]:
        """解析MetalPriceAPI返回的数据"""
        try:
            if 'rates' in data and 'CNY' in data['rates']:
                price_cny_per_oz = data['rates']['CNY']
                price_cny_per_gram = price_cny_per_oz / 31.1035
                return {
                    'price': round(price_cny_per_gram, 2),
                    'raw_data': data
                }
        except Exception as e:
            logging.error(f"解析MetalPriceAPI数据失败: {e}")
        return None

    def get_gold_price_from_api(self) -> Optional[Dict]:
        """从API获取黄金价格"""
        for api in self.api_endpoints:
            try:
                logging.info(f"尝试从 {api['name']} 获取数据...")
                response = self.session.get(api['url'], params=api['params'], timeout=10)
                response.raise_for_status()

                data = response.json()
                parsed_data = api['parser'](data)

                if parsed_data:
                    return {
                        'source': api['name'],
                        'price': parsed_data['price'],
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': parsed_data['raw_data'],
                        'note': '国际黄金价格，仅供参考'
                    }

            except Exception as e:
                logging.error(f"从 {api['name']} 获取数据失败: {e}")
                continue

        return None

    def get_shuibei_approximate_price(self) -> Dict:
        """获取水贝市场近似金价（基于国际金价+加工费估算）"""
        api_price = self.get_gold_price_from_api()

        if api_price:
            # 水贝金价通常比国际金价高一些（包含加工费、利润等）
            shuibei_price = api_price['price'] * 1.08  # 增加8%作为估算
            return {
                'source': f"{api_price['source']} (估算)",
                'price': round(shuibei_price, 2),
                'timestamp': datetime.now().isoformat(),
                'base_international_price': api_price['price'],
                'markup_percentage': 8.0,
                'note': '基于国际金价估算的水贝市场金价，实际价格可能有所不同'
            }
        else:
            return {
                'source': 'API数据源',
                'price': None,
                'timestamp': datetime.now().isoformat(),
                'error': '无法从API获取基准金价'
            }


# 兼容原有接口的函数
def get_real_gold_price():
    """获取真实黄金价格"""
    api = GoldPriceAPI()
    return api.get_shuibei_approximate_price()


if __name__ == "__main__":
    # 测试API
    logging.basicConfig(level=logging.INFO)

    api = GoldPriceAPI()
    result = api.get_shuibei_approximate_price()
    print("API获取结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
