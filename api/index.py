# index.py - Vercel 主入口文件
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入FastAPI应用
try:
    from web_api import app

    # 定义处理函数（Vercel Serverless 需要）
    handler = app

except Exception as e:
    # 创建降级应用
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="股票数据API (降级模式)")


    @app.get("/")
    async def root():
        return JSONResponse({
            "status": "running",
            "message": "主模块加载失败，使用降级模式",
            "error": str(e)
        })


    handler = app