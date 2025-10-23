import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from typing import Dict, Optional

from real_gold_price import get_real_gold_price

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gold_price.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ShuiBeiGoldPriceScraper:
    """水贝黄金价格爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

        # 可能的水贝金价数据源
        self.data_sources = [
            {
                'name': '上海黄金交易所',
                'url': 'https://www.sge.com.cn/goldPrice',
                'description': '上海黄金交易所官方价格'
            },
            {
                'name': '中国黄金网',
                'url': 'https://www.gold.org.cn/',
                'description': '中国黄金网实时金价'
            },
            {
                'name': '金投网-实时金价',
                'url': 'https://quote.cngold.org/gold/cngold.html',
                'description': '金投网实时金价'
            }
        ]

    def get_shuibei_price_from_gold_org(self) -> Optional[Dict]:
        """从黄金网获取水贝金价"""
        try:
            response = self.session.get(self.data_sources[0]['url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 这里需要根据实际网页结构调整选择器
            # 示例选择器，需要根据实际网站调整
            price_elements = soup.find_all('div', class_='gold-price') or \
                           soup.find_all('span', class_='price') or \
                           soup.find_all('td', text=lambda x: x and '水贝' in x)

            if price_elements:
                # 提取价格信息
                price_text = price_elements[0].get_text().strip()
                return {
                    'source': self.data_sources[0]['name'],
                    'price': self._extract_price(price_text),
                    'timestamp': datetime.now().isoformat(),
                    'raw_text': price_text
                }

        except Exception as e:
            logging.error("从黄金网获取水贝金价失败: %s", e)

        return None

    def get_shuibei_price_from_cngold(self) -> Optional[Dict]:
        """从金投网获取水贝金价"""
        try:
            response = self.session.get(self.data_sources[1]['url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找包含水贝金价的元素
            price_elements = soup.find_all(text=lambda x: x and '水贝' in x)

            for element in price_elements:
                parent = element.parent
                if parent:
                    price_text = parent.get_text().strip()
                    price = self._extract_price(price_text)
                    if price:
                        return {
                            'source': self.data_sources[1]['name'],
                            'price': price,
                            'timestamp': datetime.now().isoformat(),
                            'raw_text': price_text
                        }

        except Exception as e:
            logging.error("从金投网获取水贝金价失败: %s", e)

        return None

    def get_shuibei_price_from_sina(self) -> Optional[Dict]:
        """从新浪财经获取黄金价格（作为备选）"""
        try:
            response = self.session.get(self.data_sources[2]['url'], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找黄金价格相关元素
            gold_elements = soup.find_all(text=lambda x: x and any(keyword in x for keyword in ['黄金', '金价', 'Au']))

            for element in gold_elements[:5]:  # 检查前几个相关元素
                price_text = element.get_text().strip()
                price = self._extract_price(price_text)
                if price:
                    return {
                        'source': self.data_sources[2]['name'],
                        'price': price,
                        'timestamp': datetime.now().isoformat(),
                        'raw_text': price_text,
                        'note': '可能不是水贝特定价格，仅供参考'
                    }

        except Exception as e:
            logging.error("从新浪财经获取黄金价格失败: %s", e)

        return None

    def _extract_price(self, text: str) -> Optional[float]:
        """从文本中提取价格数字"""
        import re

        # 匹配价格模式：数字+可能的小数点+可能的后缀
        patterns = [
            r'(\d+\.?\d*)\s*元/克',
            r'¥\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*元',
            r'价格\s*[:：]\s*(\d+\.?\d*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    def get_gold_price(self) -> Dict:
        """获取水贝金价，尝试多个数据源"""
        logging.info("开始获取水贝金价...")

        # 首先尝试使用API获取真实数据
        try:
            api_price = get_real_gold_price()
            if api_price and api_price.get('price'):
                logging.info("从API成功获取水贝金价估算: %s元/克", api_price['price'])
                return api_price
        except Exception as e:
            logging.warning("API获取失败，尝试网页数据源: %s", e)

        # 如果API失败，按优先级尝试不同的网页数据源
        price_data = None

        # 首先尝试金投网
        price_data = self.get_shuibei_price_from_cngold()
        if price_data:
            logging.info("从金投网成功获取水贝金价: %s元/克", price_data['price'])
            return price_data

        # 然后尝试黄金网
        price_data = self.get_shuibei_price_from_gold_org()
        if price_data:
            logging.info("从黄金网成功获取水贝金价: %s元/克", price_data['price'])
            return price_data

        # 最后尝试新浪财经作为备选
        price_data = self.get_shuibei_price_from_sina()
        if price_data:
            logging.info("从新浪财经获取黄金价格: %s元/克", price_data['price'])
            return price_data

        # 如果所有数据源都失败
        error_msg = "无法从任何数据源获取水贝金价"
        logging.error(error_msg)
        return {
            'source': '所有数据源',
            'price': None,
            'timestamp': datetime.now().isoformat(),
            'error': error_msg
        }


if __name__ == "__main__":
    # 测试代码
    scraper = ShuiBeiGoldPriceScraper()
    result = scraper.get_gold_price()
    print(json.dumps(result, ensure_ascii=False, indent=2))
