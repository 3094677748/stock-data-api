# stock_code.py - 股票名称转代码
class StockCodeConverter:
    def __init__(self):
        # 创建股票名称到代码的映射字典
        self.stock_dict = {
            # A股
            "贵州茅台": "600519",
            "茅台": "600519",
            "五粮液": "000858",
            "宁德时代": "300750",
            "比亚迪": "002594",
            "中国平安": "601318",
            "招商银行": "600036",
            "中信证券": "600030",
            "东方财富": "300059",
            "万科A": "000002",
            "格力电器": "000651",

            # 港股
            "腾讯控股": "00700",
            "腾讯": "00700",
            "阿里巴巴": "09988",
            "美团": "03690",
            "小米集团": "01810",

            # 美股
            "苹果": "AAPL",
            "苹果公司": "AAPL",
            "微软": "MSFT",
            "谷歌": "GOOGL",
            "特斯拉": "TSLA",
            "亚马逊": "AMZN",
            "英伟达": "NVDA",

            # 指数
            "上证指数": "000001",
            "深证成指": "399001",
            "创业板指": "399006",
            "沪深300": "000300"
        }

    def name_to_code(self, stock_name):
        """将股票名称转换为股票代码"""
        # 先直接查找
        if stock_name in self.stock_dict:
            return self.stock_dict[stock_name]

        # 模糊匹配（包含关系）
        for name, code in self.stock_dict.items():
            if stock_name in name or name in stock_name:
                return code

        # 没找到返回None
        return None

    def add_stock(self, name, code):
        """添加新的股票映射"""
        self.stock_dict[name] = code
        print(f"已添加股票映射：{name} -> {code}")

    def list_stocks(self):
        """列出所有支持的股票"""
        print("支持的股票列表：")
        for name, code in self.stock_dict.items():
            print(f"  {name:15} -> {code}")


# 测试代码
if __name__ == "__main__":
    converter = StockCodeConverter()

    # 测试
    test_names = ["贵州茅台", "腾讯", "苹果", "测试股票"]
    for name in test_names:
        code = converter.name_to_code(name)
        if code:
            print(f"✓ {name} -> {code}")
        else:
            print(f"✗ 未找到股票：{name}")

    converter.list_stocks()