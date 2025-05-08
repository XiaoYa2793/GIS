@echo off
echo 正在启动北京旅游文化体验系统...

echo 启动后端服务...
start cmd /k "cd backend && python app.py"

echo 启动前端服务...
start cmd /k "cd frontend && npm run dev"

echo 应用已启动，请在浏览器中访问前端应用
echo 前端地址通常是: http://localhost:5173
echo 后端API地址: http://localhost:5000

echo 按任意键退出...
pause > nul 