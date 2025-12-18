# test_api.py - 测试API
import requests
import json


def test_local_api():
    """测试本地API"""
    base_url = "http://localhost:8000"

    # 测试1: 根路径
    print("测试1: 根路径")
    response = requests.get(f"{base_url}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    # 测试2: 健康检查
    print("\n测试2: 健康检查")
    response = requests.get(f"{base_url}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    # 测试3: 获取股票数据
    print("\n测试3: 获取股票数据")
    stock_name = "贵州茅台"
    response = requests.get(f"{base_url}/api/stock/{stock_name}")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"股票: {data['stock_name']}")
        print(f"成功: {data['success']}")
        print(f"数据条数: {data['metadata']['days']}")
        print(f"最新价格: {data['summary']['price']['close']}")
    else:
        print(f"错误: {response.json()}")

    # 测试4: 带参数获取
    print("\n测试4: 带参数获取")
    response = requests.get(f"{base_url}/api/stock/贵州茅台?days=5")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"实际获取天数: {data['metadata']['days']}")
        print(f"日期范围: {data['metadata']['date_range']['start']} 到 {data['metadata']['date_range']['end']}")


def test_stock_api_module():
    """直接测试股票API模块"""
    from stock_api import StockDataAPI

    api = StockDataAPI()

    # 测试搜索
    print("测试搜索功能:")
    matches = api.search_stock("茅台")
    print(f"搜索'茅台'找到 {len(matches)} 个结果:")
    for match in matches:
        print(f"  {match['name']} ({match['code']}) - {match['type']}")

    # 测试获取数据
    print("\n测试获取数据:")
    result = api.get_stock_data("贵州茅台", 10)

    if result["success"]:
        print(f"获取 {result['stock_name']} 成功")
        print(f"股票代码: {result['stock_code']}")
        print(f"数据条数: {len(result['data'])}")
        print(f"技术指标: RSI={result['summary']['rsi']['value']:.2f}")

        # 显示前3条数据
        print("\n前3条数据:")
        for i in range(min(3, len(result['data']))):
            item = result['data'][i]
            print(f"  {item['date']}: 开{item['open']:.2f}, 收{item['close']:.2f}")
    else:
        print(f"失败: {result['message']}")


if __name__ == "__main__":
    print("选择测试方式:")
    print("1. 测试本地API服务（需要先运行web_api.py）")
    print("2. 直接测试股票API模块")

    choice = input("请输入选择 (1 或 2): ").strip()

    if choice == "1":
        print("\n测试本地API服务...")
        test_local_api()
    elif choice == "2":
        print("\n直接测试股票API模块...")
        test_stock_api_module()
    else:
        print("无效选择")