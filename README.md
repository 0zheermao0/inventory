# 库存管理系统

一个基于Vue.js和Django的现代化库存管理系统，具备商品管理、出入库记录和报表打印功能。

## 功能特性

- 商品管理（增删改查）
- 入库/出库操作
- 交易记录查询和筛选
- 报表打印功能（支持选择特定记录打印）
- 现代化UI界面
- 热门商品推荐和搜索优化

## 技术栈

- 前端：Vue 3 + Element Plus
- 后端：Django + Django REST Framework
- 数据库：SQLite（默认）
- 报表生成：ReportLab

## 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

## 安装和运行

### 后端（Django）

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务器
python manage.py runserver
```

### 前端（Vue.js）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式运行
npm run dev
```

## 中文打印支持

为了支持中文打印，系统会尝试使用SimHei字体。如果需要打印中文报表，请执行以下步骤：

1. 下载SimHei.ttf字体文件
2. 将字体文件放置在 `backend/fonts/` 目录下
3. 确保文件名为 `SimHei.ttf`

如果未提供中文字体文件，系统将使用默认英文字体，中文可能会显示为方块。

## 使用说明

1. 启动后端服务（默认端口8000）
2. 启动前端服务（默认端口8080）
3. 访问 http://localhost:8080
4. 默认管理员账户：admin / admin123

## 功能说明

### 商品管理
- 添加、编辑、删除商品
- 搜索商品（按编号或名称）

### 出入库管理
- 选择商品进行入库或出库操作
- 热门商品推荐（点击选择框时显示）
- 搜索商品（支持模糊搜索）
- 自动填充商品单价

### 报表打印
- 打印所有记录
- 选择特定记录打印
- 支持中文（需提供中文字体文件）

## API接口

- 商品管理：`/api/products/`
- 库存记录：`/api/inventory-transactions/`
- 报表打印：`/api/inventory-transactions/print_report/`

## 目录结构

```
.
├── backend/              # Django后端
│   ├── products/         # 商品管理模块
│   ├── inventory/        # 库存管理模块
│   ├── inventory_system/ # 项目配置
│   ├── manage.py         # Django管理脚本
│   └── requirements.txt  # Python依赖
└── frontend/             # Vue前端
    ├── src/              # 源代码
    ├── public/           # 静态资源
    └── package.json      # npm配置
```# inventory
