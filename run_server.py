# run_server.py - 单独的启动文件
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("股票数据API服务启动中...")
    print("访问 http://localhost:8000 查看API文档")
    print("访问 http://localhost:8000/api/stock/贵州茅台 测试接口")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)

    # 使用字符串形式导入
    uvicorn.run(
        "web_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 现在可以使用reload了
    )