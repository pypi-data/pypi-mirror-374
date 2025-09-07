# visAIon

VisAIon 是一个全功能的计算机视觉 AI 平台，提供从数据管理到模型训练、部署的完整解决方案。

## 安装

### 环境要求
- Python 3.10+
- Conda (推荐)

### 从 PyPI 安装
```bash
# 创建虚拟环境
conda create -n visaion python=3.10
conda activate visaion

# 安装 visaion
pip install visaionserver -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 visaionlibrary 库（包含 CUDA 支持）
# ⚠️ 强烈建议安装 `visaionlibrary` 库时，不要修改指定的源
# ⚠️ 安装过程可能耗时较长，请耐心等待
# ⚠️ 确保网络连接稳定，避免下载中断
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
  -f https://download.openmmlab.com/mmcv/dist/cu117/torch1.13/index.html \
  --extra-index-url https://download.pytorch.org/whl/cu117 \
  visaionlibrary
```

## 快速开始

### 启动服务
```bash
visaion start   # 启动服务器
```

服务启动后，在浏览器中访问 `http://localhost:8000` 即可使用 Web 界面。

### 基本命令
```bash
visaion status   # 检查服务状态
visaion stop     # 停止服务
visaion logs     # 查看日志位置
visaion version  # 查看版本信息
visaion settings # 查看当前配置
```

### 数据管理
```bash
# 配置数据存储目录
# ⚠️ 把下面"/your/custom/path"替换要安装的目录, 目录最好选择空间大些、有读写权限的目录
VISAION_DIR=/your/custom/path
visaion settings visaion_dir=$VISAION_DIR

# cd到数据存储目录
cd $VISAION_DIR

# 下载预训练模版
wget -O templates.zip https://cdn.visaion.cc/templates/1.0.2/templates.zip

# 下载预训练权重
wget -O weights.zip https://cdn.visaion.cc/weights/1.0.0/weights.zip
```

## 主要功能

- **项目管理**: 创建和管理计算机视觉项目
- **数据集管理**: 上传、标注和管理训练数据
- **模型训练**: 支持主流的目标检测、分类算法
- **模型评估**: 完整的模型性能评估工具
- **模型导出**: 支持 ONNX 等格式的模型导出
- **Web 界面**: 直观易用的 Web 管理界面

## API 文档

服务启动后，可通过以下地址访问 API 文档：
- Swagger UI: `http://localhost:8000/docs`

## 技术支持

如有问题或建议，可以通过邮箱 fa.fu@visaion.cc 联系我们。
