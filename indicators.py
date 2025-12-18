# indicators.py - 计算技术指标
import pandas as pd
import numpy as np


class IndicatorCalculator:
    def __init__(self):
        pass

    def calculate_all(self, df):
        """
        计算所有技术指标
        Args:
            df: 包含date, open, high, low, close, volume的DataFrame
        Returns:
            添加了技术指标的DataFrame
        """
        if df is None or len(df) < 5:
            print("数据不足，无法计算技术指标")
            return df

        print(f"开始计算技术指标，数据量：{len(df)}条")

        # 复制数据，避免修改原始数据
        result = df.copy()

        # 计算各种技术指标
        result = self._calculate_ma(result)  # 移动平均线
        result = self._calculate_rsi(result)  # RSI
        result = self._calculate_macd(result)  # MACD
        result = self._calculate_kdj(result)  # KDJ

        # 计算价格变化
        result = self._calculate_price_change(result)

        print("技术指标计算完成")
        return result

    def _calculate_ma(self, df):
        """计算移动平均线"""
        # 计算5日、10日、20日、60日移动平均线
        df['MA5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['MA10'] = df['close'].rolling(window=10, min_periods=1).mean()
        df['MA20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['MA60'] = df['close'].rolling(window=60, min_periods=1).mean()

        # 计算价格与均线的关系
        df['above_MA5'] = df['close'] > df['MA5']
        df['above_MA10'] = df['close'] > df['MA10']
        df['above_MA20'] = df['close'] > df['MA20']

        return df

    def _calculate_rsi(self, df, period=14):
        """计算RSI（相对强弱指数）"""
        # 计算价格变化
        delta = df['close'].diff()

        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # 计算平均上涨和平均下跌
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()

        # 计算相对强度（RS）
        rs = avg_gain / avg_loss
        rs = rs.replace([np.inf, -np.inf], 100)  # 处理除以0的情况

        # 计算RSI
        df['RSI'] = 100 - (100 / (1 + rs))

        # 添加RSI信号
        df['RSI_overbought'] = df['RSI'] > 70  # 超买
        df['RSI_oversold'] = df['RSI'] < 30  # 超卖

        return df

    def _calculate_macd(self, df):
        """计算MACD指标"""
        # 计算12日EMA
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        # 计算26日EMA
        exp2 = df['close'].ewm(span=26, adjust=False).mean()

        # MACD线（快线 - 慢线）
        df['MACD'] = exp1 - exp2
        # 信号线（MACD的9日EMA）
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        # MACD柱状图
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']

        # 添加MACD信号
        df['MACD_golden_cross'] = (df['MACD'] > df['MACD_signal']) & (df['MACD'].shift(1) <= df['MACD_signal'].shift(1))
        df['MACD_death_cross'] = (df['MACD'] < df['MACD_signal']) & (df['MACD'].shift(1) >= df['MACD_signal'].shift(1))

        return df

    def _calculate_kdj(self, df, n=9, m1=3, m2=3):
        """计算KDJ指标"""
        # 计算n日最低价
        low_min = df['low'].rolling(window=n, min_periods=1).min()
        # 计算n日最高价
        high_max = df['high'].rolling(window=n, min_periods=1).max()

        # 计算RSV（未成熟随机值）
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        rsv = rsv.replace([np.inf, -np.inf], 50)  # 处理除以0的情况

        # 计算K值（RSV的m1日指数移动平均）
        df['K'] = rsv.ewm(alpha=1 / m1, adjust=False).mean()
        # 计算D值（K值的m2日指数移动平均）
        df['D'] = df['K'].ewm(alpha=1 / m2, adjust=False).mean()
        # 计算J值
        df['J'] = 3 * df['K'] - 2 * df['D']

        # 添加KDJ信号
        df['KDJ_golden_cross'] = (df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1))
        df['KDJ_death_cross'] = (df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1))
        df['K_overbought'] = df['K'] > 80
        df['K_oversold'] = df['K'] < 20

        return df

    def _calculate_price_change(self, df):
        """计算价格变化"""
        if len(df) > 1:
            df['price_change'] = df['close'].pct_change() * 100
            df['price_change_5d'] = df['close'].pct_change(periods=5) * 100

        return df

    def get_indicators_summary(self, df):
        """获取技术指标摘要"""
        if df is None or len(df) == 0:
            return {}

        latest = df.iloc[-1]

        summary = {
            "price": {
                "close": float(latest['close']) if 'close' in df.columns else None,
                "change": float(latest['price_change']) if 'price_change' in df.columns else None,
                "change_5d": float(latest['price_change_5d']) if 'price_change_5d' in df.columns else None,
            },
            "moving_averages": {
                "MA5": float(latest['MA5']) if 'MA5' in df.columns else None,
                "MA10": float(latest['MA10']) if 'MA10' in df.columns else None,
                "MA20": float(latest['MA20']) if 'MA20' in df.columns else None,
                "MA60": float(latest['MA60']) if 'MA60' in df.columns else None,
                "above_MA20": bool(latest['above_MA20']) if 'above_MA20' in df.columns else None,
            },
            "rsi": {
                "value": float(latest['RSI']) if 'RSI' in df.columns else None,
                "status": "超买" if 'RSI' in df.columns and latest['RSI'] > 70 else
                "超卖" if 'RSI' in df.columns and latest['RSI'] < 30 else "正常"
            },
            "macd": {
                "value": float(latest['MACD']) if 'MACD' in df.columns else None,
                "signal": float(latest['MACD_signal']) if 'MACD_signal' in df.columns else None,
                "hist": float(latest['MACD_hist']) if 'MACD_hist' in df.columns else None,
                "signal_text": "金叉看多" if 'MACD_golden_cross' in df.columns and latest['MACD_golden_cross'] else
                "死叉看空" if 'MACD_death_cross' in df.columns and latest['MACD_death_cross'] else "中性"
            },
            "kdj": {
                "K": float(latest['K']) if 'K' in df.columns else None,
                "D": float(latest['D']) if 'D' in df.columns else None,
                "J": float(latest['J']) if 'J' in df.columns else None,
                "status": "超买" if 'K' in df.columns and latest['K'] > 80 else
                "超卖" if 'K' in df.columns and latest['K'] < 20 else "正常"
            }
        }

        return summary


# 测试代码
if __name__ == "__main__":
    import numpy as np

    # 创建测试数据
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    df = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 100)
    })

    calculator = IndicatorCalculator()

    # 计算技术指标
    df_with_indicators = calculator.calculate_all(df)

    print("原始数据形状：", df.shape)
    print("添加指标后形状：", df_with_indicators.shape)

    # 查看最后几行
    print("\n最后5行数据（带技术指标）：")
    print(df_with_indicators.tail())

    # 获取技术指标摘要
    summary = calculator.get_indicators_summary(df_with_indicators)

    print("\n技术指标摘要：")
    print(f"收盘价：{summary['price']['close']:.2f}")
    print(f"RSI：{summary['rsi']['value']:.2f} ({summary['rsi']['status']})")
    print(f"MACD：{summary['macd']['value']:.4f} ({summary['macd']['signal_text']})")
    print(f"是否在20日均线上方：{summary['moving_averages']['above_MA20']}")