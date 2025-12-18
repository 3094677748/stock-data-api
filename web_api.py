# web_api.py - 完整修正版
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入你的数据模块
try:
    from stock_code import StockCodeConverter
    from kline_fetcher import KlineFetcher
    from indicators import IndicatorCalculator
    from stock_api import StockDataAPI

    print("✅ 成功导入股票数据模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")


    # 定义空类作为备用
    class StockDataAPI:
        def __init__(self):
            pass

        def get_stock_data(self, *args, **kwargs):
            return {"success": False, "message": "模块未正确导入"}

# 创建FastAPI应用
app = FastAPI(
    title="股票数据API服务",
    description="为金融智能体提供股票数据和技术指标",
    version="1.0.0"
)

# 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建API实例
api = StockDataAPI()


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "service": "股票数据API",
        "version": "1.0.0",
        "endpoints": {
            "/api/stock": "获取所有股票列表",  # 新增
            "/api/stock/{name}": "获取单只股票数据",
            "/health": "健康检查",
            "/test": "测试接口"
        },
        "status": "运行正常",
        "note": "访问 /api/stock 获取股票列表，或 /api/stock/贵州茅台 获取股票数据"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "stock_data_api"}


@app.get("/test")
async def test():
    """测试接口"""
    return {"message": "API服务正常运行", "test": "success"}


@app.get("/api/stock")
async def list_stocks():
    """
    获取所有支持的股票列表
    访问 http://localhost:8000/api/stock 即可调用
    """
    try:
        stocks = []
        # 遍历您在 stock_code.py 中定义的股票字典
        for name, code in api.converter.stock_dict.items():
            # 判断股票类型
            if code.isdigit() and len(code) == 6:
                stock_type = "A股"
            elif code.startswith('0') and len(code) == 5:
                stock_type = "港股"
            else:
                stock_type = "美股"

            stocks.append({
                "name": name,
                "code": code,
                "type": stock_type
            })

        # 按类型和名称排序，使列表更有序
        stocks.sort(key=lambda x: (x["type"], x["name"]))

        return {
            "success": True,
            "message": f"共支持 {len(stocks)} 只股票",
            "data": stocks,
            "count": len(stocks),
            "types": {
                "a_share": len([s for s in stocks if s["type"] == "A股"]),
                "hk_share": len([s for s in stocks if s["type"] == "港股"]),
                "us_share": len([s for s in stocks if s["type"] == "美股"])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")


@app.get("/api/stock/{stock_name}")
async def get_stock(
        stock_name: str,
        days: int = 30
):
    """
    获取单只股票数据
    - stock_name: 股票名称，如"贵州茅台"
    - days: 天数，默认30天
    """
    try:
        result = api.get_stock_data(stock_name, days)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# 本地运行部分 - 修改这里！
if __name__ == "__main__":
    print("=" * 60)
    print("股票数据API服务启动中...")
    print("访问 http://localhost:8000 查看API文档")
    print("访问 http://localhost:8000/api/stock 获取股票列表")
    print("访问 http://localhost:8000/api/stock/贵州茅台 测试接口")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)

    # 方法1：简单方式，去掉reload
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )

    # 或者方法2：使用字符串形式（如果你需要热重载）
    # uvicorn.run("web_api:app", host="0.0.0.0", port=8000, reload=True)