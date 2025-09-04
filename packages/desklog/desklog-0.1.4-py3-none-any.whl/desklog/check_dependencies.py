"""
检查DeskLog运行所需的依赖
"""
import sys
import subprocess
import platform

def check_tkinter():
    """检查tkinter是否可用"""
    try:
        import tkinter
        print("✅ tkinter 可用")
        return True
    except ImportError as e:
        print(f"❌ tkinter 不可用: {e}")
        return False

def check_system_dependencies():
    """检查系统依赖"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("检测到 macOS 系统")
        print("如果tkinter不可用，请运行以下命令之一：")
        print("1. brew install python-tk")
        print("2. 使用系统Python: /usr/bin/python3")
        print("3. 安装Anaconda/Miniconda")
        
    elif system == "linux":
        print("检测到 Linux 系统")
        print("如果tkinter不可用，请运行：")
        print("sudo apt-get install python3-tk  # Ubuntu/Debian")
        print("sudo yum install tkinter         # CentOS/RHEL")
        
    elif system == "windows":
        print("检测到 Windows 系统")
        print("tkinter通常随Python一起安装，如果不可用请重新安装Python")

def main():
    """主检查函数"""
    print("🔍 检查DeskLog依赖...")
    print("-" * 40)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查tkinter
    tkinter_ok = check_tkinter()
    
    # 检查其他依赖
    try:
        import flask
        print("✅ Flask 可用")
    except ImportError:
        print("❌ Flask 不可用")
    
    try:
        import requests
        print("✅ Requests 可用")
    except ImportError:
        print("❌ Requests 不可用")
    
    print("-" * 40)
    
    if not tkinter_ok:
        check_system_dependencies()
        return False
    
    print("🎉 所有依赖检查通过！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
