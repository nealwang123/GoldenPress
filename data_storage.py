import json
import csv
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd

class GoldPriceStorage:
    """黄金价格数据存储类"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.json_file = os.path.join(data_dir, "gold_prices.json")
        self.csv_file = os.path.join(data_dir, "gold_prices.csv")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 初始化数据文件
        self._initialize_files()
    
    def _initialize_files(self):
        """初始化数据文件"""
        # JSON文件初始化
        if not os.path.exists(self.json_file):
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # CSV文件初始化
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'source', 'price', 'raw_text', 'error', 'note'
                ])
    
    def save_price_data(self, price_data: Dict):
        """保存价格数据到所有格式"""
        # 添加保存时间戳
        price_data['saved_at'] = datetime.now().isoformat()
        
        # 保存到JSON
        self._save_to_json(price_data)
        
        # 保存到CSV
        self._save_to_csv(price_data)
        
        print(f"价格数据已保存: {price_data.get('price', 'N/A')}元/克")
    
    def _save_to_json(self, price_data: Dict):
        """保存数据到JSON文件"""
        try:
            # 读取现有数据
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 添加新数据
            data.append(price_data)
            
            # 只保留最近1000条记录以避免文件过大
            if len(data) > 1000:
                data = data[-1000:]
            
            # 写回文件
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存到JSON文件失败: {e}")
    
    def _save_to_csv(self, price_data: Dict):
        """保存数据到CSV文件"""
        try:
            with open(self.csv_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    price_data.get('timestamp', ''),
                    price_data.get('source', ''),
                    price_data.get('price', ''),
                    price_data.get('raw_text', ''),
                    price_data.get('error', ''),
                    price_data.get('note', '')
                ])
                
        except Exception as e:
            print(f"保存到CSV文件失败: {e}")
    
    def get_recent_prices(self, limit: int = 10) -> List[Dict]:
        """获取最近的价格数据"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data[-limit:]
            
        except Exception as e:
            print(f"读取价格数据失败: {e}")
            return []
    
    def get_price_statistics(self) -> Dict:
        """获取价格统计信息"""
        try:
            # 使用pandas读取CSV文件进行统计分析
            df = pd.read_csv(self.csv_file)
            
            # 过滤有效价格数据
            valid_prices = df[df['price'].notna() & (df['price'] != '')]
            
            if len(valid_prices) == 0:
                return {
                    'total_records': len(df),
                    'valid_price_records': 0,
                    'message': '没有有效的价格数据'
                }
            
            # 转换价格列为数值类型
            valid_prices['price'] = pd.to_numeric(valid_prices['price'])
            
            stats = {
                'total_records': len(df),
                'valid_price_records': len(valid_prices),
                'current_price': valid_prices['price'].iloc[-1],
                'min_price': valid_prices['price'].min(),
                'max_price': valid_prices['price'].max(),
                'avg_price': valid_prices['price'].mean(),
                'price_std': valid_prices['price'].std(),
                'data_sources': valid_prices['source'].value_counts().to_dict(),
                'latest_update': valid_prices['timestamp'].iloc[-1]
            }
            
            return stats
            
        except Exception as e:
            print(f"生成统计信息失败: {e}")
            return {'error': str(e)}
    
    def export_to_excel(self, output_file: str = None):
        """导出数据到Excel文件"""
        if output_file is None:
            output_file = os.path.join(self.data_dir, "gold_prices_export.xlsx")
        
        try:
            df = pd.read_csv(self.csv_file)
            df.to_excel(output_file, index=False)
            print(f"数据已导出到: {output_file}")
            
        except Exception as e:
            print(f"导出到Excel失败: {e}")
    
    def clear_old_data(self, days: int = 30):
        """清理指定天数前的旧数据"""
        try:
            df = pd.read_csv(self.csv_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            filtered_df = df[df['timestamp'] >= cutoff_date]
            
            # 保存过滤后的数据
            filtered_df.to_csv(self.csv_file, index=False)
            
            # 同时更新JSON文件
            with open(self.json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            filtered_json = [
                record for record in json_data 
                if pd.to_datetime(record['timestamp']) >= cutoff_date
            ]
            
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_json, f, ensure_ascii=False, indent=2)
            
            print(f"已清理 {days} 天前的数据，剩余 {len(filtered_df)} 条记录")
            
        except Exception as e:
            print(f"清理数据失败: {e}")
    
    def clear_all_data(self):
        """清除所有历史数据"""
        try:
            # 清空JSON文件
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            # 清空CSV文件，只保留表头
            with open(self.csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'source', 'price', 'raw_text', 'error', 'note'
                ])
            
            print("✅ 已清除所有历史数据")
            
        except Exception as e:
            print(f"清除数据失败: {e}")


if __name__ == "__main__":
    # 测试代码
    storage = GoldPriceStorage()
    
    # 测试数据
    test_data = {
        'source': '测试数据源',
        'price': 480.5,
        'timestamp': datetime.now().isoformat(),
        'raw_text': '测试价格 480.5元/克'
    }
    
    storage.save_price_data(test_data)
    
    # 获取统计信息
    stats = storage.get_price_statistics()
    print("统计信息:", json.dumps(stats, ensure_ascii=False, indent=2))
    
    # 获取最近记录
    recent = storage.get_recent_prices(5)
    print("最近5条记录:", json.dumps(recent, ensure_ascii=False, indent=2))
