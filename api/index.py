# api/index.py - Vercel Serverless 函数入口
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(
    title="股票数据API服务",
    description="为金融智能体提供股票数据和技术指标",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 基础路由 ====================
@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "service": "股票数据API",
        "version": "1.0.0",
        "status": "运行正常",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "/": "API信息",
            "/health": "健康检查",
            "/test": "测试接口",
            "/api/stock": "获取所有股票列表",
            "/api/stock/{name}": "获取单只股票数据"
        },
        "example": {
            "get_stock": "/api/stock/贵州茅台?days=10",
            "list_stocks": "/api/stock"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "stock_data_api",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


@app.get("/test")
async def test():
    """测试接口"""
    return {
        "message": "API服务正常运行",
        "test": "success",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


# ==================== 股票数据路由 ====================
@app.get("/api/stock")
async def list_stocks(
        search: Optional[str] = None,
        type: Optional[str] = None
):
    """
    获取股票列表
    - search: 搜索关键词（可选）
    - type: 股票类型：a_share, hk_share, us_share（可选）
    """
    try:
        # 延迟导入，避免启动时失败
        from stock_code import StockCodeConverter
        converter = StockCodeConverter()

        stocks = []
        for name, code in converter.stock_dict.items():
            # 判断股票类型
            if code.isdigit() and len(code) == 6:
                stock_type = "a_share"
            elif code.startswith('0') and len(code) == 5:
                stock_type = "hk_share"
            else:
                stock_type = "us_share"

            # 筛选
            if search and search.lower() not in name.lower() and search.lower() not in code.lower():
                continue
            if type and stock_type != type:
                continue

            stocks.append({
                "name": name,
                "code": code,
                "type": stock_type,
                "display_name": f"{name} ({code})"
            })

        # 按类型和名称排序
        stocks.sort(key=lambda x: (x["type"], x["name"]))

        return {
            "success": True,
            "message": f"找到 {len(stocks)} 只股票",
            "data": stocks,
            "count": len(stocks),
            "types": {
                "a_share": len([s for s in stocks if s["type"] == "a_share"]),
                "hk_share": len([s for s in stocks if s["type"] == "hk_share"]),
                "us_share": len([s for s in stocks if s["type"] == "us_share"])
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取股票列表失败: {str(e)}"
        )


@app.get("/api/stock/{stock_name}")
async def get_stock(
        stock_name: str,
        days: int = 30
):
    """
    获取单只股票数据
    - stock_name: 股票名称，如"贵州茅台"
    - days: 天数，默认30天，最大100天
    """
    # 限制天数
    if days > 100:
        days = 100
    if days < 1:
        days = 1

    try:
        # 延迟导入，避免启动时失败
        from stock_api import StockDataAPI
        api = StockDataAPI()
        result = api.get_stock_data(stock_name, days)

        if not result.get("success", False):
            raise HTTPException(
                status_code=404,
                detail=result.get("message", f"未找到股票 {stock_name}")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取股票数据失败: {str(e)}"
        )


@app.get("/api/stock/{stock_name}/simple")
async def get_stock_simple(
        stock_name: str,
        days: int = 10
):
    """
    获取股票数据（简化版）
    - 仅返回关键信息，适合快速查看
    """
    try:
        # 延迟导入
        from stock_api import StockDataAPI
        api = StockDataAPI()
        result = api.get_stock_data(stock_name, min(days, 30))

        if not result.get("success", False):
            return {
                "success": False,
                "message": result.get("message", "获取数据失败"),
                "stock_name": stock_name
            }

        # 提取关键信息
        summary = result.get("summary", {})
        price_info = summary.get("price", {})

        simple_data = {
            "success": True,
            "stock_name": result.get("stock_name"),
            "stock_code": result.get("stock_code"),
            "price": price_info.get("close"),
            "change": price_info.get("change"),
            "summary": {
                "rsi": summary.get("rsi", {}).get("value"),
                "rsi_status": summary.get("rsi", {}).get("status"),
                "macd_signal": summary.get("macd", {}).get("signal_text"),
                "above_ma20": summary.get("moving_averages", {}).get("above_MA20")
            },
            "data_points": result.get("metadata", {}).get("days", 0)
        }

        return simple_data

    except Exception as e:
        return {
            "success": False,
            "message": f"获取数据失败: {str(e)}",
            "stock_name": stock_name
        }


# ==================== 错误处理 ====================
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": f"资源未找到: {request.url.path}",
            "suggestions": [
                "检查URL路径是否正确",
                "访问 / 查看所有可用端点",
                "访问 /api/stock 查看支持的股票列表"
            ]
        }
    )


@app.exception_handler(500)
async def server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error": str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        }
    )


# ==================== Vercel 必要导出 ====================
from fastapi.responses import JSONResponse

handler = app