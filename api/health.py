# api/health.py - 最简单的健康检查函数
from fastapi import FastAPI

# 创建应用
app = FastAPI(title="健康检查API", version="1.0.0")

@app.get("/")
async def root():
    return {"status": "ok", "service": "stock-api", "message": "健康检查API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.now().isoformat()}

# Vercel需要的导出
handler = app