# 水贝黄金价格实时监控系统配置说明

## 系统概述

这是一个用于获取水贝黄金实时价格的Python程序，包含多种数据源和灵活的配置选项。

## 当前状态

当前系统使用市场估算数据作为备用方案，因为：
- 网络访问限制导致部分网站无法访问
- 免费API有调用限制
- 银行网站需要特定的解析逻辑

## 获取真实数据的配置方法

### 1. 使用真实API数据源

编辑 `real_gold_price.py` 文件，取消注释以下代码块：

```python
# 尝试银行数据源
try:
    from bank_gold_price import get_bank_gold_data
    bank_data = get_bank_gold_data()
    if bank_data and bank_data.get('price'):
        return bank_data
except Exception as e:
    logging.warning(f"银行数据源失败: {e}")

# 尝试API数据源
try:
    from gold_api import get_real_gold_price
    api_data = get_real_gold_price()
    if api_data and api_data.get('price'):
        return api_data
except Exception as e:
    logging.warning(f"API数据源失败: {e}")
```

### 2. 配置API密钥

对于 `gold_api.py` 中的API，需要获取真实的API密钥：

- **Alpha Vantage**: 访问 https://www.alphavantage.co/support/#api-key 注册获取免费API密钥
- **MetalPriceAPI**: 访问 https://metalpriceapi.com/ 注册获取API密钥

### 3. 银行数据源配置

`bank_gold_price.py` 中的银行数据源需要根据实际网页结构调整解析逻辑：

- 工商银行: 需要分析实际的JSON响应格式
- 中国银行: 需要分析HTML页面结构
- 建设银行: 需要分析HTML页面结构

### 4. 网页爬虫配置

编辑 `gold_price_scraper.py` 中的数据源URL和解析逻辑：

```python
self.data_sources = [
    {
        'name': '上海黄金交易所',
        'url': 'https://www.sge.com.cn/goldPrice',
        'description': '上海黄金交易所官方价格'
    },
    # 添加更多数据源...
]
```

## 运行模式

### 单次获取
```bash
python main.py single
```

### 定时监控
```bash
python main.py monitor
```

### 查看统计
```bash
python main.py stats
```

## 数据存储

价格数据保存在 `gold_prices.json` 文件中，包含：
- 价格数值
- 数据来源
- 时间戳
- 原始文本

## 注意事项

1. **网络访问**: 确保网络环境可以访问目标网站
2. **API限制**: 免费API通常有调用频率限制
3. **网页结构变化**: 网站改版时需要更新解析逻辑
4. **法律合规**: 确保爬虫使用符合网站robots.txt和法律法规

## 扩展建议

1. 添加更多可靠的数据源
2. 实现数据验证和异常处理
3. 添加邮件/短信通知功能
4. 创建Web界面展示数据
5. 集成数据库存储

## 故障排除

如果获取失败，检查：
- 网络连接
- 防火墙设置
- 网站是否可访问
- API密钥是否有效
- 解析逻辑是否正确
