# api/index.py - Vercel专用入口
import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 导入你的FastAPI应用
try:
    # 注意：这里导入的是web_api中的app
    from web_api import app

    # 可选：调整一些配置
    app.title = "股票数据API (Vercel部署版)"
    app.description = "部署在Vercel的股票数据服务，团队成员可直接访问"

    # 确保CORS配置正确
    from fastapi.middleware.cors import CORSMiddleware

    if not any(middleware.__class__.__name__ == "CORSMiddleware"
               for middleware in app.user_middleware):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    print("✅ API应用加载成功")

except ImportError as e:
    print(f"❌ 导入失败: {e}")

    # 创建紧急备用应用
    from fastapi import FastAPI

    app = FastAPI()


    @app.get("/")
    async def emergency_root():
        return {
            "error": "主应用加载失败",
            "check": "请确保web_api.py在同一目录下"
        }