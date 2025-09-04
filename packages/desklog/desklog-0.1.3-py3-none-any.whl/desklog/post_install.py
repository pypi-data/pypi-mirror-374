"""
DeskLog 安装后脚本
自动检查和安装tkinter依赖
"""
import sys
import subprocess
import platform
import os

def install_tkinter_macos():
    """在macOS上安装tkinter支持"""
    try:
        # 检查是否已安装python-tk
        result = subprocess.run(['brew', 'list', 'python-tk'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ python-tk 已安装")
            return True
        
        print("🔄 正在安装 python-tk...")
        result = subprocess.run(['brew', 'install', 'python-tk'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ python-tk 安装成功")
            return True
        else:
            print(f"❌ python-tk 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装 python-tk 时出错: {e}")
        return False

def install_tkinter_linux():
    """在Linux上安装tkinter支持"""
    try:
        # 检测发行版并安装相应的包
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu
            cmd = ['sudo', 'apt-get', 'update']
            subprocess.run(cmd, check=True)
            cmd = ['sudo', 'apt-get', 'install', '-y', 'python3-tk']
        elif os.path.exists('/etc/redhat-release'):
            # CentOS/RHEL
            cmd = ['sudo', 'yum', 'install', '-y', 'tkinter']
        else:
            print("❌ 不支持的Linux发行版")
            return False
        
        print("🔄 正在安装 tkinter 支持...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ tkinter 支持安装成功")
            return True
        else:
            print(f"❌ tkinter 支持安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安装 tkinter 支持时出错: {e}")
        return False

def check_tkinter():
    """检查tkinter是否可用"""
    try:
        import tkinter
        print("✅ tkinter 可用")
        return True
    except ImportError:
        print("❌ tkinter 不可用")
        return False

def main():
    """主函数"""
    print("🔧 DeskLog 安装后配置...")
    print("=" * 40)
    
    # 检查tkinter
    if check_tkinter():
        print("🎉 所有依赖已就绪！")
        return True
    
    # 根据系统安装tkinter
    system = platform.system().lower()
    success = False
    
    if system == "darwin":  # macOS
        print("🍎 检测到 macOS 系统")
        success = install_tkinter_macos()
    elif system == "linux":
        print("🐧 检测到 Linux 系统")
        success = install_tkinter_linux()
    elif system == "windows":
        print("🪟 检测到 Windows 系统")
        print("Windows 系统通常包含 tkinter，如果不可用请重新安装 Python")
        success = True
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return False
    
    if success:
        print("\n🎉 配置完成！现在可以运行: desklog")
    else:
        print("\n❌ 自动配置失败，请手动安装依赖")
        print("macOS: brew install python-tk")
        print("Linux: sudo apt-get install python3-tk")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
