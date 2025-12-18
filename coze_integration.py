# coze_integration.py - 扣子平台调用示例

import requests
import json


class CozeStockAPI:
    """扣子平台调用股票API的示例"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def get_stock_for_coze(self, stock_name, days=30):
        """
        为扣子平台获取股票数据（简化版）
        返回格式化的文本，适合在聊天中显示
        """
        try:
            # 调用自己的API
            url = f"{self.base_url}/api/stock/{stock_name}"
            params = {"days": days}

            response = requests.get(url, params=params)
            data = response.json()

            if not data.get("success", False):
                return f"获取 {stock_name} 数据失败：{data.get('message', '未知错误')}"

            summary = data.get("summary", {})

            # 构建适合在聊天中显示的文本
            result = f"📊 **{stock_name}** 股票分析报告\n"
            result += "=" * 40 + "\n"

            if "price" in summary:
                price_info = summary["price"]
                result += f"💰 当前价格: {price_info.get('close', 'N/A')}\n"
                if price_info.get('change'):
                    change = price_info['change']
                    change_icon = "📈" if change > 0 else "📉"
                    result += f"{change_icon} 涨跌幅: {change:.2f}%\n"

            result += "\n📈 技术指标:\n"

            if "rsi_status" in summary and summary["rsi_status"].get("RSI"):
                rsi = summary["rsi_status"]["RSI"]
                rsi_status = ""
                if rsi > 70:
                    rsi_status = " (超买⚠️)"
                elif rsi < 30:
                    rsi_status = " (超卖⚠️)"
                result += f"  • RSI: {rsi:.2f}{rsi_status}\n"

            if "ma_status" in summary:
                ma = summary["ma_status"]
                if ma.get("above_MA20"):
                    result += f"  • 股价在20日均线之上 ✅\n"
                else:
                    result += f"  • 股价在20日均线之下 ⚠️\n"

            if "macd_status" in summary and summary["macd_status"].get("MACD"):
                macd = summary["macd_status"]["MACD"]
                signal = summary["macd_status"].get("signal", 0)
                if macd > signal:
                    result += f"  • MACD金叉看多 ✅\n"
                else:
                    result += f"  • MACD死叉看空 ⚠️\n"

            result += "\n🎯 综合信号:\n"
            if "signals" in summary:
                signals = summary["signals"]
                if signals.get("bullish"):
                    result += "  • 总体看涨信号较强 🚀\n"
                elif signals.get("bearish"):
                    result += "  • 总体看跌信号较强 ⚠️\n"
                else:
                    result += "  • 中性信号 ↔️\n"

            # 添加数据来源
            result += f"\n📅 数据期间: {data.get('metadata', {}).get('date_range', {}).get('start', '')} 至 "
            result += f"{data.get('metadata', {}).get('date_range', {}).get('end', '')}\n"
            result += f"📊 数据条数: {data.get('metadata', {}).get('days', 0)} 条\n"

            return result

        except Exception as e:
            return f"调用API失败：{str(e)}"


# 测试代码
if __name__ == "__main__":
    # 确保Web服务正在运行（python web_api.py）
    coze_api = CozeStockAPI()

    # 测试几只股票
    test_stocks = ["贵州茅台", "腾讯", "苹果"]

    for stock in test_stocks:
        print("\n" + "=" * 60)
        print(f"扣子平台调用示例 - {stock}")
        print("=" * 60)

        result = coze_api.get_stock_for_coze(stock, days=20)
        print(result)