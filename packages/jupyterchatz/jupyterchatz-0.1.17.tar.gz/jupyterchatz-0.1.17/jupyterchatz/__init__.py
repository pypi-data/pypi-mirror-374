from ._version import __version__
import os
import sys
import shutil
import site
from pathlib import Path

# 直接在__init__.py中实现安装逻辑
def install_labextension():
    """安装JupyterLab扩展文件"""
    try:
        # 获取包的安装路径
        package_dir = Path(__file__).parent.absolute()
        labextension_dir = package_dir / "labextension"
        
        # 获取site-packages目录
        site_packages = site.getsitepackages()[0]
        
        # 创建目标目录
        target_dir = Path(site_packages) / "share" / "jupyter" / "labextensions" / "jupyterchatz"
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        if labextension_dir.exists():
            # 复制所有文件
            for item in labextension_dir.glob("**/*"):
                if item.is_file():
                    relative_path = item.relative_to(labextension_dir)
                    target_file = target_dir / relative_path
                    os.makedirs(target_file.parent, exist_ok=True)
                    shutil.copy2(item, target_file)
            
            # 创建install.json文件
            install_json_path = target_dir / "install.json"
            with open(install_json_path, 'w') as f:
                f.write('{\n')
                f.write('  "packageManager": "python",\n')
                f.write('  "packageName": "jupyterchatz",\n')
                f.write('  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterchatz"\n')
                f.write('}\n')
            
            print(f"JupyterLab扩展文件已安装到 {target_dir}")
        else:
            print(f"找不到扩展文件: {labextension_dir}")
    except Exception as e:
        print(f"安装JupyterLab扩展时出错: {e}", file=sys.stderr)

# 尝试安装扩展
try:
    # 只在安装包时运行，不在开发模式下运行
    if not os.environ.get('JUPYTERCHATZ_DEV_MODE'):
        install_labextension()
except Exception as e:
    print(f"警告: 安装JupyterLab扩展时出错: {e}", file=sys.stderr)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "jupyterchatz"
    }]
