# 🔍 Android View Scope

> 现代化的Android UI元素检查器，类似weditor的功能，基于Vue.js 3 + FastAPI构建

## ✨ 特性

- 🚀 **现代化技术栈** - Vue.js 3 + Element Plus + FastAPI
- [DEVICE]**设备管理** - 自动检测和管理Android设备
- 🖼️ **实时截图** - 高质量PNG截图获取
- 🎯 **交互式元素选择** - SVG交互层，点击选择UI元素
- 📊 **UI层次结构** - 完整的界面层次树显示
- 💻 **代码生成** - 自动生成uiautomator2定位代码
- 🔧 **多种定位策略** - Resource-ID、文本、XPath等多种方式

## 🏗️ 项目结构

```
viewscope/
├── frontend/          # Vue.js 3 前端项目
│   ├── src/
│   │   ├── views/     # 页面组件
│   │   ├── stores/    # 状态管理 (Pinia)
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
├── backend/           # FastAPI 后端项目  
│   ├── main.py        # 应用入口
│   ├── core/          # 核心模块
│   │   ├── device_manager.py  # 设备管理
│   │   ├── ui_analyzer.py     # UI分析
│   │   └── code_generator.py  # 代码生成
│   ├── api/           # API路由
│   │   ├── devices.py
│   │   ├── screenshot.py
│   │   └── ...
│   └── requirements.txt
├── start.bat          # 一键启动脚本
└── README.md
```

## 🚀 快速开始

### 一键启动 (推荐)

双击运行 `start.bat` 脚本，会自动：
1. 启动后端API服务 (端口8000)
2. 安装前端依赖 (如果需要)
3. 启动前端开发服务器 (端口8080)

### 手动启动

#### 后端启动
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 📋 前置要求

### 系统要求
- Windows 10/11
- Python 3.8+
- Node.js 16+
- 已安装Android SDK (ADB可用)

### 设备要求
- Android 4.4+
- 开启USB调试
- 设备已通过ADB连接

### 验证环境
```bash
# 检查Python
python --version

# 检查Node.js
node --version

# 检查ADB
adb version

# 检查设备连接
adb devices
```

## 🎯 使用方法

1. **启动应用**
   - 运行 `start.bat` 或手动启动前后端
   - 浏览器打开 http://localhost:8080

2. **连接设备**
   - 在顶部工具栏选择设备
   - 点击"刷新当前视图"按钮

3. **元素选择**
   - 在截图上点击任意UI元素
   - 右侧面板显示元素详细信息

4. **代码生成**
   - 切换到"代码生成"标签页
   - 查看自动生成的uiautomator2代码
   - 点击"复制代码"按钮

5. **UI层次查看**
   - 切换到"UI层次"标签页
   - 浏览完整的界面树状结构
   - 使用搜索功能定位特定元素

## 🔧 API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要接口

- `GET /api/devices` - 获取设备列表
- `POST /api/screenshot` - 截图并获取UI结构
- `GET /api/ui-hierarchy` - 获取UI层次结构
- `POST /api/code/generate` - 生成定位代码

## 🐛 故障排除

### 常见问题

1. **设备检测不到**
   ```bash
   # 检查ADB连接
   adb devices
   # 重启ADB服务
   adb kill-server
   adb start-server
   ```

2. **截图失败**
   - 确保设备已授权USB调试
   - 检查设备是否锁屏
   - 尝试重新连接设备

3. **前端无法访问后端**
   - 检查后端是否在8000端口启动
   - 确认防火墙设置
   - 查看浏览器控制台错误

4. **依赖安装失败**
   ```bash
   # Python依赖
   pip install -r requirements.txt -i https://pypi.douban.com/simple
   
   # Node.js依赖  
   npm install --registry=https://registry.npm.taobao.org
   ```

## 🛠️ 开发说明

### 技术栈
- **前端**: Vue.js 3, Element Plus, SVG, Pinia
- **后端**: FastAPI, uiautomator2, Pillow
- **构建工具**: Vite, Python uvicorn

### 开发环境
```bash
# 后端热重载
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端热重载
npm run dev
```

## 📦 构建部署

### 前端构建
```bash
cd frontend
npm run build
```

### 后端打包
```bash
cd backend
pip install pyinstaller
pyinstaller --onefile main.py
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [uiautomator2](https://github.com/openatx/uiautomator2) - Android自动化框架
- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架  
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Element Plus](https://element-plus.org/) - Vue.js UI组件库

---

如有问题或建议，欢迎提Issue或Pull Request！