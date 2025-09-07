from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# 从pyproject.toml读取版本号保持一致
def get_version():
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            # Python 3.11+ 使用内置 tomllib
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                # Python 3.10 使用 tomli
                import tomli as tomllib
            
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "0.0.0")
        except ImportError:
            # 如果tomli未安装，fallback到简单解析
            with open(pyproject_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        return line.split('"')[1]
    return "0.0.0"

# 确保包含PyArmor运行时库
packages = find_packages(where='dist')
if 'pyarmor_runtime_000000' not in packages:
    packages.append('pyarmor_runtime_000000')

setup(
    name="visaionserver",
    version=get_version(),
    # 仅处理PyArmor特殊逻辑，其他配置由pyproject.toml处理
    package_dir={'': 'dist'},
    packages=packages,
    # 为PyArmor运行时添加额外的包数据
    package_data={
        'pyarmor_runtime_000000': [
            '__init__.py',
            'pyarmor_runtime.pyd',
            'pyarmor_runtime.so',
            '*.so', 
            '*.pyd',
            '*.dll', 
            '*.dylib'
        ],
    },
    # 标记为包含扩展模块以支持平台特定的wheel
    has_ext_modules=lambda: True,
) 