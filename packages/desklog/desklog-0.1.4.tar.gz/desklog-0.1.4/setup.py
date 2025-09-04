from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import subprocess
import platform
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def post_install():
    """安装后的配置函数"""
    try:
        # 检查tkinter是否可用
        import tkinter
        print("✅ tkinter 已可用")
        return True
    except ImportError:
        print("🔧 检测到 tkinter 不可用，正在尝试自动安装...")
        
        system = platform.system().lower()
        if system == "darwin":  # macOS
            try:
                # 检查是否已安装python-tk
                result = subprocess.run(['brew', 'list', 'python-tk'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print("🔄 正在安装 python-tk...")
                    result = subprocess.run(['brew', 'install', 'python-tk'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ python-tk 安装成功")
                        return True
                    else:
                        print(f"❌ python-tk 安装失败: {result.stderr}")
                        return False
                else:
                    print("✅ python-tk 已安装")
                    return True
            except Exception as e:
                print(f"❌ 安装 python-tk 时出错: {e}")
                return False
        elif system == "linux":
            try:
                if os.path.exists('/etc/debian_version'):
                    cmd = ['sudo', 'apt-get', 'update']
                    subprocess.run(cmd, check=True)
                    cmd = ['sudo', 'apt-get', 'install', '-y', 'python3-tk']
                else:
                    print("❌ 不支持的Linux发行版")
                    return False
                
                print("🔄 正在安装 python3-tk...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ python3-tk 安装成功")
                    return True
                else:
                    print(f"❌ python3-tk 安装失败: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ 安装 python3-tk 时出错: {e}")
                return False
        else:
            print("❌ 不支持的操作系统")
            return False

# 自定义安装命令
class CustomInstallCommand(install):
    """自定义安装命令，在安装后执行配置"""
    def run(self):
        install.run(self)
        post_install()

setup(
    name="desklog",
    version="0.1.4",
    author="ymqz1988",
    author_email="ymqz1988@gmail.com",
    description="A desktop logging application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/desklog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": ["desklog=desklog.server:start"]
    },
    # 安装后执行配置
    cmdclass={
        'install': CustomInstallCommand,
    },
)

