#!/bin/bash
echo "开始部署股票数据API到Vercel..."

# 1. 安装Vercel CLI
npm install -g vercel

# 2. 登录Vercel（如果需要）
# vercel login

# 3. 部署项目
vercel --prod

echo "部署完成！"