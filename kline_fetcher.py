# kline_fetcher.py - 获取K线数据（兼容Vercel部署）
import pandas as pd
from datetime import datetime, timedelta
import random
import yfinance as yf


class KlineFetcher:
    def __init__(self):
        self.code_converter = None

    def set_converter(self, converter):
        """设置代码转换器"""
        self.code_converter = converter

    def get_kline_data(self, stock_name, days=30):
        """
        获取股票的K线数据
        Args:
            stock_name: 股票名称
            days: 交易天数
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        if not self.code_converter:
            return None

        # 1. 转换股票名称
        stock_code = self.code_converter.name_to_code(stock_name)
        if not stock_code:
            print(f"错误：未找到股票 {stock_name}")
            return self._get_mock_data(stock_name, days)

        print(f"正在获取 {stock_name}({stock_code}) 的K线数据...")

        try:
            # 2. 根据股票类型获取数据
            if stock_code.isdigit() and len(stock_code) == 6:
                # A股
                return self._get_a_stock(stock_code, days)
            elif stock_code.startswith('0') and len(stock_code) == 5:
                # 港股
                return self._get_hk_stock(stock_code, days)
            else:
                # 美股或其他
                return self._get_other_stock(stock_code, days)
        except Exception as e:
            print(f"获取数据失败：{e}")
            return self._get_mock_data(stock_name, days)  # 返回模拟数据

    def _get_a_stock(self, stock_code, days):
        """获取A股数据（使用yfinance）"""
        # A股在yfinance中的代码格式：代码.SS（上证）或代码.SZ（深证）
        if stock_code.startswith('6'):
            ticker_symbol = f"{stock_code}.SS"  # 上证
        else:
            ticker_symbol = f"{stock_code}.SZ"  # 深证

        return self._get_yfinance_data(ticker_symbol, days, "A股")

    def _get_hk_stock(self, stock_code, days):
        """获取港股数据（使用yfinance）"""
        # 港股在yfinance中的代码格式：代码.HK
        ticker_symbol = f"{stock_code}.HK"
        return self._get_yfinance_data(ticker_symbol, days, "港股")

    def _get_other_stock(self, stock_code, days):
        """获取其他股票数据（使用yfinance）"""
        return self._get_yfinance_data(stock_code, days, "美股")

    def _get_yfinance_data(self, ticker_symbol, days, market_type):
        """使用yfinance获取数据"""
        try:
            print(f"使用yfinance获取{market_type}数据，代码: {ticker_symbol}")

            ticker = yf.Ticker(ticker_symbol)

            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days * 2)  # 多获取一些数据

            # 获取历史数据
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                raise ValueError(f"未获取到 {ticker_symbol} 的数据")

            # 重置索引，将Date变为列
            df = df.reset_index()

            # 重命名列
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # 选择需要的列
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]

            # 转换日期格式
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')

            # 排序并取最近的days天
            df = df.sort_values('date')
            if len(df) > days:
                df = df.tail(days)

            print(f"成功获取 {len(df)} 条{market_type}数据")
            return df

        except Exception as e:
            print(f"yfinance获取{market_type}数据失败: {e}")
            raise

    def _get_mock_data(self, stock_name, days):
        """获取模拟数据（当真实API失败时使用）"""
        print(f"使用模拟数据替代 {stock_name}")

        import random
        from datetime import datetime, timedelta

        data = []
        today = datetime.now()

        # 生成模拟数据
        base_price = 100 + random.uniform(-50, 50)

        for i in range(days):
            date = today - timedelta(days=days - i - 1)

            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + random.uniform(-5, 5)
            high_price = max(open_price, close_price) + random.uniform(0, 3)
            low_price = min(open_price, close_price) - random.uniform(0, 3)

            # 确保价格为正数
            open_price = max(0.01, open_price)
            close_price = max(0.01, close_price)
            high_price = max(0.01, high_price)
            low_price = max(0.01, low_price)

            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': random.randint(1000000, 10000000)
            })

        return pd.DataFrame(data)


# 测试代码
if __name__ == "__main__":
    from stock_code import StockCodeConverter

    converter = StockCodeConverter()
    fetcher = KlineFetcher()
    fetcher.set_converter(converter)

    # 测试获取数据
    stocks = ["贵州茅台", "腾讯", "苹果"]

    for stock in stocks:
        print(f"\n获取 {stock} 的数据：")
        data = fetcher.get_kline_data(stock, days=5)

        if data is not None:
            print(data)
            print(f"数据形状：{data.shape}")
            print(f"最新收盘价：{data['close'].iloc[-1] if len(data) > 0 else 'N/A'}")
        else:
            print("获取数据失败")