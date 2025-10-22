# 水贝黄金价格实时监控系统

一个用于获取深圳水贝市场实时黄金价格的Python程序，支持定时监控、数据存储和统计分析。

## 功能特性

- 🔍 **实时获取**：从多个数据源获取水贝市场实时金价
- ⏰ **定时监控**：支持每分钟自动获取价格数据
- 💾 **数据存储**：自动保存历史数据到JSON和CSV格式
- 📊 **统计分析**：提供价格统计、趋势分析等功能
- 📤 **数据导出**：支持导出到Excel格式
- 🛡️ **异常处理**：完善的错误处理和日志记录

## 安装依赖

```bash
# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 单次获取价格
```bash
python main.py single
```

### 启动定时监控（每分钟一次）
```bash
python main.py schedule
```

### 每5分钟获取一次
```bash
python main.py schedule --interval 5
```

### 查看统计信息
```bash
python main.py stats
```

### 测试数据源连接
```bash
python main.py test
```

### 导出数据到Excel
```bash
python main.py export
```

### 显示帮助信息
```bash
python main.py help
```

## 项目结构

```
py_getGoldenPress/
├── main.py                 # 主程序入口
├── gold_price_scraper.py   # 价格爬虫模块
├── data_storage.py         # 数据存储模块
├── scheduler.py            # 定时任务调度器
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明
└── data/                  # 数据存储目录（自动创建）
    ├── gold_prices.json   # JSON格式价格数据
    └── gold_prices.csv    # CSV格式价格数据
```

## 数据源

程序尝试从以下数据源获取水贝金价：

1. **金投网-深圳水贝** (`https://quote.cngold.org/gold/shuibeijia.html`)
2. **黄金网-水贝金价** (`https://www.gold.org.cn/`)
3. **新浪财经-黄金** (`https://finance.sina.com.cn/money/nmetal/hjzx/`)

## 输出格式

程序返回的JSON格式数据示例：
```json
{
  "source": "金投网-深圳水贝",
  "price": 485.5,
  "timestamp": "2025-10-22T17:05:30.123456",
  "raw_text": "水贝金价 485.5元/克"
}
```

## 注意事项

1. **网络连接**：需要稳定的网络连接来获取实时数据
2. **数据准确性**：价格数据来源于第三方网站，仅供参考
3. **使用限制**：请遵守各数据源的使用条款，避免频繁请求
4. **时间间隔**：建议设置合理的获取间隔，避免对服务器造成压力

## 故障排除

### 常见问题

1. **获取失败**：检查网络连接和数据源网站是否可访问
2. **价格解析错误**：数据源网站结构可能发生变化，需要更新解析规则
3. **依赖安装失败**：确保使用正确的Python版本（建议Python 3.8+）

### 日志文件

程序运行日志保存在 `gold_price.log` 文件中，可用于排查问题。

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和数据源的使用条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
