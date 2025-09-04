# visAIon
VisAIon，"Vision(视觉)" 和 "AI" 的融合，代表着视觉 AI 技术引领行业发展, 拥有前瞻性的视野与目标, 视觉AI一站式平台

## 版本说明
```
x.y.z
x: 表示主版本号, 当架构或组件有重大变化是修改主版本号
y: 表示次版本号, 当修改bug, 增加新特性时, 修改次版本号
z: 表示标志版本号, 0表示未加密, 1表示加密
```

## 如何安装
开发模式
```
conda create -n visaion python=3.10
conda activate visaion
git clone https://gitee.com/QiShi_1/visaionserver.git
cd visaionserver
pip install --upgrade build
bash build_wheel_unencrypted.sh (for linux)
build_wheel_unencrypted.bat (for windows)
pip install -e .
```

生产模式(未加密)
```
conda create -n visaion python=3.10
conda activate visaion
pip install --force-reinstall visaionserver-* -i https://pypi.tuna.tsinghua.edu.cn/simple

```

生产模式(加密)
```
conda create -n visaion python=3.10
conda activate visaion
pip install --force-reinstall visaionserver-* -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 如何启动&停止
```
visaion start   # 启动, 启动后需要在浏览器中访问
visaion status  # 状态
visaion stop    # 停止

```

## 如何打包

打包未加密版本
```
pip install --upgrade build
bash build_wheel_unencrypted.sh (for linux)
build_wheel_unencrypted.bat (for windows)
```

打包加密版本
```
pip install --upgrade build
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyarmor==9.1.1 pyarmor.cli.core==7.6.4 pyarmor.cli==9.1.2

临时修改pyproject.toml文件的version字段, 加密版本z版本为1, 同时修改setup文件

# 生成runtime
pyarmor gen runtime -O ../pyarmor_runtime

bash build_wheel_encrypted.sh (for linux)
build_wheel_encrypted.bat (for windows)
```

## FastAPI 项目结构

### 目录结构
```
visaionserver/
├── __init__.py
├── api/                    # API 路由
│   ├── __init__.py
│   ├── deps.py            # 依赖注入
│   └── v1/                # API v1 版本
│       ├── __init__.py
│       ├── auth.py         # 登录管理接口
│       ├── datasets.py     # 数据集管理接口
│       ├── evaluation.py   # 模型评估接口
│       ├── inference.py    # 模型推理接口
│       ├── models.py       # AI模型训练管理接口
│       ├── projects.py     # 项目管理接口
│       ├── samples.py      # 样本管理接口
│       ├── job_scheduler.py # 任务调度接口
│       └── job_resources.py # 资源管理接口
├── models/                 # 数据库模型
│   ├── __init__.py
│   ├── ai_model.py        # AI模型训练模型类
│   ├── datasets.py        # 数据集模型类
│   ├── project.py         # 项目模型
│   ├── sample.py          # 样本模型
│   └── user.py            # 用户模型
├── schemas/               # Pydantic 模型，用于请求/响应验证
│   ├── __init__.py
│   ├── common.py          # 公共的请求响应模型
│   ├── project.py         # 项目相关的请求响应模型
│   ├── sample.py          # 样本相关的请求响应模型
│   └── user.py            # 用户相关的请求响应模型
├── services/              # 业务逻辑
│   ├── __init__.py
│   ├── auth.py            # 认证服务
│   ├── project.py         # 项目服务
│   └── sample.py          # 样本服务
├── core/                  # 核心配置
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── settings.py        # 系统设置
│   └── security.py        # 安全相关
├── db/                    # 数据库相关
│   ├── __init__.py
│   └── session.py         # 数据库会话管理
└── utils/                 # 工具函数
    ├── __init__.py
    └── common.py          # 通用工具
```

### 主要组件说明

#### 1. API 路由 (`visaionserver/api/`)
- 采用版本化的 API 结构 (v1)
- 使用 FastAPI 路由器进行模块化管理
- 实现 RESTful API 接口

#### 2. 数据模型 (`visaionserver/models/` & `visaionserver/schemas/`)
- `models/`: SQLAlchemy ORM 模型，用于数据库交互
- `schemas/`: Pydantic 验证模型，用于请求/响应数据验证
- 严格的类型检查和数据验证

#### 3. 业务逻辑 (`visaionserver/services/`)
- 封装核心业务逻辑
- 实现数据处理和业务规则
- 保持与路由层的解耦

#### 4. 核心配置 (`visaionserver/core/`)
- 管理系统配置和环境变量
- 处理安全相关的功能（认证、授权）
- 系统设置管理

#### 5. 数据库管理 (`visaionserver/db/`)
- 数据库连接和会话管理
- 数据库配置和迁移

#### 6. 工具函数 (`visaionserver/utils/`)
- 提供通用工具函数
- 实现跨模块共享的功能
- 提供辅助方法和工具类

### 开发规范

#### 代码风格
- 使用 Python 类型注解
- 遵循 PEP 8 编码规范
- 采用函数式编程范式

#### 异步处理
- 使用 `async/await` 处理 I/O 密集型操作
- 数据库操作采用异步客户端
- 避免阻塞操作影响性能

#### 错误处理
- 统一的异常处理机制
- 详细的错误日志记录
- 友好的错误响应格式

### 环境配置

#### 依赖安装
```
bash
pip install -r requirements.txt
```

#### 环境变量
创建 `.env` 文件并配置以下变量：
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
API_VERSION=v1
DEBUG=True  
```

#### 启动项目
```
bash
uvicorn app.main:app --reload
```

### API 文档
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API 接口说明 (api/v1/)

#### 1. 登录认证管理 (auth.py)
- `POST /api/v1/auth/login`: 用户登录
  - 请求体: username, password
  - 响应: access_token, token_type
- `GET /api/v1/auth/me`: 获取当前用户信息
  - 请求头: Authorization: Bearer {token}
  - 响应: 用户详细信息
- `POST /api/v1/auth/refresh`: 刷新访问令牌
  - 请求头: Authorization: Bearer {token}
  - 响应: 新的 access_token
- `POST /api/v1/auth/logout`: 用户登出
  - 请求头: Authorization: Bearer {token}
  - 响应: 登出成功状态

#### 2. 数据集管理 (datasets.py)
- `GET /api/v1/datasets`: 获取数据集列表
- `POST /api/v1/datasets`: 创建新数据集
- `GET /api/v1/datasets/{dataset_id}`: 获取特定数据集详情
- `PUT /api/v1/datasets/{dataset_id}`: 更新数据集信息
- `DELETE /api/v1/datasets/{dataset_id}`: 删除数据集
- `POST /api/v1/datasets/{dataset_id}/samples`: 向数据集添加样本

#### 3. 样本管理 (samples.py)
- `GET /api/v1/samples`: 获取样本列表
- `POST /api/v1/samples`: 上传新样本
- `GET /api/v1/samples/{sample_id}`: 获取样本详情
- `PUT /api/v1/samples/{sample_id}`: 更新样本信息
- `DELETE /api/v1/samples/{sample_id}`: 删除样本
- `POST /api/v1/samples/{sample_id}/annotations`: 添加样本标注

#### 4. AI 模型管理 (models.py)
- `GET /api/v1/models`: 获取模型列表
- `POST /api/v1/models`: 注册新模型
- `GET /api/v1/models/{model_id}`: 获取模型详情
- `PUT /api/v1/models/{model_id}`: 更新模型信息
- `DELETE /api/v1/models/{model_id}`: 删除模型
- `POST /api/v1/models/{model_id}/versions`: 上传新版本
- `POST /api/v1/models/{model_id}/predict`: 模型推理接口

#### 5. 任务调度管理 (job_scheduler.py)
- `GET /api/v1/jobs`: 获取任务列表
- `POST /api/v1/jobs`: 创建新任务
- `GET /api/v1/jobs/{job_id}`: 获取任务详情
- `PUT /api/v1/jobs/{job_id}`: 更新任务状态
- `DELETE /api/v1/jobs/{job_id}`: 删除任务
- `POST /api/v1/jobs/{job_id}/cancel`: 取消正在运行的任务

#### 6. 资源管理 (job_resources.py)
- `GET /api/v1/resources`: 获取资源使用情况
- `GET /api/v1/resources/gpu`: 获取 GPU 资源状态
- `GET /api/v1/resources/memory`: 获取内存使用情况
- `GET /api/v1/resources/storage`: 获取存储使用情况

#### 7. 项目管理 (projects.py)
- `GET /api/v1/projects`: 获取项目列表
- `POST /api/v1/projects`: 创建新项目
- `GET /api/v1/projects/{project_id}`: 获取项目详情
- `PUT /api/v1/projects/{project_id}`: 更新项目信息
- `DELETE /api/v1/projects/{project_id}`: 删除项目
- `GET /api/v1/projects/{project_id}/datasets`: 获取项目关联的数据集
- `POST /api/v1/projects/{project_id}/datasets`: 关联数据集到项目
- `GET /api/v1/projects/{project_id}/models`: 获取项目关联的模型
- `POST /api/v1/projects/{project_id}/models`: 关联模型到项目
- `GET /api/v1/projects/{project_id}/members`: 获取项目成员列表
- `POST /api/v1/projects/{project_id}/members`: 添加项目成员
- `DELETE /api/v1/projects/{project_id}/members/{user_id}`: 移除项目成员

### 开发建议

#### 1. 接口实现规范
- 使用 Pydantic 模型进行请求和响应验证
- 实现统一的错误处理机制
- 添加详细的接口文档注释
- 实现接口访问权限控制

#### 2. 示例代码结构
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.dataset import DatasetCreate, DatasetResponse
from app.services.dataset import DatasetService
from app.deps import get_current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    dataset_service: DatasetService = Depends()
):
    """获取数据集列表"""
    return await dataset_service.get_datasets(skip=skip, limit=limit, user_id=current_user.id)

@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    dataset: DatasetCreate,
    current_user = Depends(get_current_user),
    dataset_service: DatasetService = Depends()
):
    """创建新数据集"""
    return await dataset_service.create_dataset(dataset=dataset, user_id=current_user.id)
```

#### 3. 异步操作处理
- 对于耗时操作使用异步处理
- 实现任务队列管理
- 提供任务进度查询接口

#### 4. 数据验证
- 使用 Pydantic 模型进行输入验证
- 实现自定义验证器
- 添加业务逻辑验证

#### 5. 安全性考虑
- 实现用户认证和授权
- 添加请求频率限制
- 实现数据访问控制
- 添加操作日志记录
