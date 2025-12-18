# 股票数据API

基于 FastAPI 构建的股票数据API服务，部署在 Vercel 上。

## 功能特性

- 📊 获取A股、港股、美股数据
- 📈 计算技术指标（RSI、MACD、KDJ、均线等）
- 🔍 股票名称智能搜索
- 🌐 支持跨域访问（CORS）
- 🚀 部署在 Vercel Serverless 环境

## API端点

### 基础端点
- `GET /` - API信息
- `GET /health` - 健康检查
- `GET /test` - 测试接口

### 股票数据端点
- `GET /api/stock` - 获取所有股票列表
- `GET /api/stock/{股票名称}` - 获取单只股票数据
- `GET /api/stock/{股票名称}/simple` - 获取简化版数据

### 查询参数
- `days` - 数据天数（默认30，最大100）
- `search` - 搜索关键词
- `type` - 股票类型（a_share, hk_share, us_share）

## 本地开发

1. 克隆项目
```bash
git clone <你的仓库地址>
cd stock-data-api