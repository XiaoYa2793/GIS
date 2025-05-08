# 北京历史地图展示系统

这个项目展示了北京从元代到现代的历史地图，展示城市的发展变迁。

## 功能特点

- **高级历史地图视图**：
  - 时间轴功能，可以切换不同时期的历史地图
  - 地图上的兴趣点标记，带有波纹动画效果
  - 可以查看不同兴趣点的详细信息
  - 地图图层控制，可以同时显示现代地图和历史地图
  - 地图对比功能，支持并排和滑动对比两种模式

- **简化版历史地图**：
  - 展示所有历史地图列表
  - 提供地图的基本信息和缩略图
  - 可以跳转到高级版本查看更多功能

## 技术栈

- **前端**：Vue 3 + Vite + Element Plus
- **后端**：Python Flask + SQLite
- **地图**：高德地图 API

## 安装和运行

### 前提条件

- Node.js 16+ 
- Python 3.7+
- 高德地图开发者Key

### 步骤

1. **克隆代码并安装依赖**

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

2. **配置高德地图Key**
   - 在 `frontend/index.html` 中替换 `securityJsCode` 和高德地图 Web 端开发者 Key
   - 在 `frontend/src/views/HistoricalMapView.vue` 中替换 `key` 值

3. **启动应用**

在Windows上，可以直接运行项目根目录下的 `start-app.bat` 批处理文件：

```bash
# 双击start-app.bat或在命令行中运行
start-app.bat
```

或者分别启动前后端：

```bash
# 启动后端
cd backend
python app.py

# 启动前端
cd frontend
npm run dev
```

4. **访问应用**

打开浏览器访问：http://localhost:5173

## 功能展示

### 历史地图高级视图

![历史地图高级视图](docs/advanced-view.png)

- 时间轴控制
- 地图图层控制
- 兴趣点标记和信息展示
- 地图对比功能

### 波纹动画效果

![波纹动画效果](docs/ripple-effect.png)

每个兴趣点都有对应类型的波纹动画，点击后会展示详细信息。

### 简化版历史地图

![简化版历史地图](docs/simple-view.png)

提供地图列表，可以快速查看每个时期的历史地图。 