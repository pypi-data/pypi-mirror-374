from setuptools import setup, find_packages
import os
import sys
import platform

# 确保包含PyArmor运行时库
packages = find_packages(where='dist')
if 'pyarmor_runtime_000000' not in packages:
    packages.append('pyarmor_runtime_000000')

# 根据当前平台设置平台特定的依赖
platform_specific_deps = []
if sys.platform.startswith('win'):
    platform_specific_deps.append("pywin32==308")

setup(
    name="visaionserver",
    version="0.2.0",  # 与pyproject.toml保持一致
    package_dir={'': 'dist'},
    packages=packages,
    package_data={
        'visaionserver': [
            '**/*.yaml', 
            '**/*.jpg',
            '**/*.png',
            '**/*.css',
            '**/*.js',
            '**/*.ico',
            '**/*.html',
            '**/*.sql',
            'static/**/*'
        ],
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
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'visaion=visaionserver.script:entrypoint',
        ],
    },
    # 添加平台特定的依赖
    install_requires=[
        "py-cpuinfo>=9.0.0",
        "psutil>=6.1.1",
        "fastapi==0.115.7",
        "uvicorn==0.34.0",
        "pynvml==12.0.0",
        "cos-python-sdk-v5==1.9.33",
        "sqlalchemy==2.0.31",
        "aiosqlite==0.20.0",
        "python-jose==3.3.0",
        "APScheduler==3.11.0",
        "email-validator==2.2.0",
        "passlib==1.7.4",
        "greenlet==3.1.1",
        "bcrypt==4.2.1",
        "Pillow==11.1.0",
        "python-multipart==0.0.20",
        "pytz==2025.1",
    ] + platform_specific_deps,
    python_requires='>=3.8',
    # Remove has_ext_modules to allow universal wheel
    has_ext_modules=lambda: True,
) 