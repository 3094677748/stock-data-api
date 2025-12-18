# stock_api.py - 主数据API
from stock_code import StockCodeConverter
from kline_fetcher import KlineFetcher
from indicators import IndicatorCalculator
import pandas as pd
import numpy as np  # 新增导入，用于处理特殊数值


class StockDataAPI:
    def __init__(self):
        print("初始化股票数据API...")

        # 初始化各个模块
        self.converter = StockCodeConverter()
        self.fetcher = KlineFetcher()
        self.fetcher.set_converter(self.converter)
        self.calculator = IndicatorCalculator()

        # 缓存
        self.cache = {}

    def _clean_dataframe(self, df):
        """
        清理DataFrame中的特殊值，使其可被JSON序列化
        将 NaN, Infinity 等替换为 None
        """
        if df is None:
            return df

        # 创建一个副本，避免修改原始数据
        df_cleaned = df.copy()

        # 1. 处理数值列：将无穷大和NaN替换为None
        # 识别数值列（排除‘date’这样的字符串列）
        numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns

        for col in numeric_columns:
            # 将无穷大值替换为None
            df_cleaned[col] = df_cleaned[col].replace([np.inf, -np.inf], None)
            # 将NaN值替换为None
            df_cleaned[col] = df_cleaned[col].where(pd.notnull(df_cleaned[col]), None)

        # 2. 确保日期列为字符串（如果存在）
        if 'date' in df_cleaned.columns:
            df_cleaned['date'] = df_cleaned['date'].astype(str)

        return df_cleaned

    def get_stock_data(self, stock_name, days=30):
        """
        获取股票数据的完整流程
        Args:
            stock_name: 股票名称
            days: 天数
        Returns:
            字典，包含数据、指标和摘要
        """
        # 检查缓存
        cache_key = f"{stock_name}_{days}"
        if cache_key in self.cache:
            print(f"使用缓存数据: {cache_key}")
            return self.cache[cache_key]

        print(f"\n{'=' * 50}")
        print(f"处理请求: {stock_name}, {days}天")

        result = {
            "success": False,
            "stock_name": stock_name,
            "message": "",
            "data": None,
            "indicators": None,
            "summary": None,
            "metadata": None
        }

        try:
            # 1. 获取K线数据
            print("1. 获取K线数据...")
            kline_data = self.fetcher.get_kline_data(stock_name, days)

            if kline_data is None or len(kline_data) == 0:
                result["message"] = "获取K线数据失败"
                return result

            # 2. 计算技术指标
            print("2. 计算技术指标...")
            data_with_indicators = self.calculator.calculate_all(kline_data)

            # 3. 获取股票代码
            stock_code = self.converter.name_to_code(stock_name)

            # 4. 获取技术指标摘要
            print("3. 生成技术指标摘要...")
            indicators_summary = self.calculator.get_indicators_summary(data_with_indicators)

            # 5. 准备返回结果（关键修改部分）
            result["success"] = True
            result["message"] = "获取数据成功"
            result["stock_code"] = stock_code

            # 清理数据中的特殊值（NaN, Infinity等）后再转换为字典
            kline_data_cleaned = self._clean_dataframe(kline_data)
            data_with_indicators_cleaned = self._clean_dataframe(data_with_indicators)

            result["data"] = kline_data_cleaned.to_dict(orient='records')
            result["indicators"] = data_with_indicators_cleaned.to_dict(orient='records')
            result["summary"] = indicators_summary
            result["metadata"] = {
                "days": len(kline_data),
                "date_range": {
                    "start": str(kline_data['date'].iloc[0]) if len(kline_data) > 0 else None,
                    "end": str(kline_data['date'].iloc[-1]) if len(kline_data) > 0 else None
                }
            }

            # 添加到缓存
            self.cache[cache_key] = result

            print(f"处理完成: 获取{len(kline_data)}条数据")

        except Exception as e:
            result["message"] = f"处理数据时出错: {str(e)}"
            print(f"错误: {e}")

        return result

    def get_multiple_stocks(self, stock_names, days=30):
        """
        获取多只股票数据
        Args:
            stock_names: 股票名称列表
            days: 天数
        Returns:
            每只股票的数据字典
        """
        results = {}

        for name in stock_names:
            print(f"\n处理股票: {name}")
            data = self.get_stock_data(name, days)
            results[name] = data

        return results

    def search_stock(self, keyword):
        """
        搜索股票
        Args:
            keyword: 搜索关键词
        Returns:
            匹配的股票列表
        """
        matches = []

        for name, code in self.converter.stock_dict.items():
            if keyword.lower() in name.lower() or keyword.lower() in code.lower():
                matches.append({
                    "name": name,
                    "code": code,
                    "type": "A股" if code.isdigit() and len(code) == 6 else
                    "港股" if code.startswith('0') and len(code) == 5 else "美股"
                })

        return matches


# 测试代码
if __name__ == "__main__":
    api = StockDataAPI()

    print("\n" + "=" * 50)
    print("测试单个股票")
    print("=" * 50)

    # 测试单个股票
    result = api.get_stock_data("贵州茅台", 10)

    if result["success"]:
        print(f"✓ 获取 {result['stock_name']} 数据成功")
        print(f"  数据条数: {result['metadata']['days']}")
        print(f"  日期范围: {result['metadata']['date_range']['start']} 到 {result['metadata']['date_range']['end']}")
        print(f"  当前价格: {result['summary']['price']['close']}")
        print(f"  RSI: {result['summary']['rsi']['value']}")
        print(f"  RSI状态: {result['summary']['rsi']['status']}")
        print(f"  MACD信号: {result['summary']['macd']['signal_text']}")
    else:
        print(f"✗ 失败: {result['message']}")

    print("\n" + "=" * 50)
    print("测试多个股票")
    print("=" * 50)

    # 测试多个股票
    stocks = ["贵州茅台", "宁德时代", "腾讯"]
    results = api.get_multiple_stocks(stocks, 5)

    for name, data in results.items():
        if data["success"]:
            print(f"✓ {name}: 价格={data['summary']['price']['close']:.2f}, RSI={data['summary']['rsi']['value']:.2f}")
        else:
            print(f"✗ {name}: {data['message']}")