"""
虚拟环境管理命令模块
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console

# 创建控制台实例
console = Console()


class VenvCommand:
    """虚拟环境命令处理类"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.venv_dir = self.project_root / ".venv"
    
    def check_uv_available(self) -> bool:
        """检查uv包管理器是否可用"""
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_package_manager(self) -> Tuple[str, str]:
        """获取包管理器 - 只支持UV"""
        if self.check_uv_available():
            return ("uv", "uv pip")
        else:
            console.print("❌ uv包管理器不可用", style="red")
            console.print("💡 请安装uv以获得更好的性能:", style="yellow")
            console.print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
            console.print("   或者使用pip安装: pip install uv")
            raise RuntimeError("UV package manager not available")
    
    def create_venv(self) -> int:
        """创建虚拟环境"""
        try:
            pkg_manager, pkg_cmd = self.get_package_manager()
        except RuntimeError:
            return 1
        
        console.print("🔄 使用uv创建虚拟环境...", style="blue")
        cmd = ["uv", "venv", ".venv"]
        
        try:
            result = subprocess.run(cmd)
            if result.returncode == 0:
                console.print("✅ 虚拟环境创建成功", style="green")
                
                # 提供激活指令
                if os.name == 'nt':  # Windows
                    console.print("如需激活虚拟环境，执行:", style="yellow")
                    console.print("    .venv\\Scripts\\activate")
                    console.print("  ")
                    console.print("安装主项目依赖运行命令：", style="green")
                    console.print("    yoapi venv install")
                else:  # Unix/Linux/Mac
                    console.print("如需激活虚拟环境，执行:", style="yellow")
                    console.print("    source .venv/bin/activate")
                    console.print("  ")
                    console.print("安装主项目依赖运行命令：", style="green")
                    console.print("    yoapi venv install")
                
                return 0
            else:
                console.print("❌ 虚拟环境创建失败", style="red")
                return 1
        except Exception as e:
            console.print(f"❌ 创建虚拟环境时出错: {e}", style="red")
            return 1
    
    def install_dependencies(self) -> int:
        """安装项目依赖"""
        try:
            pkg_manager, pkg_cmd = self.get_package_manager()
        except RuntimeError:
            return 1
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            console.print("❌ requirements.txt 文件不存在", style="red")
            console.print("💡 请确保在项目根目录下存在 requirements.txt 文件", style="yellow")
            return 1
        
        console.print("📦 正在安装项目依赖...", style="blue")
        console.print(f"📄 使用文件: {requirements_file}", style="blue")
        
        # 构建安装命令
        if pkg_manager == "uv":
            cmd = ["uv", "pip", "install", "-r", "requirements.txt"]
        else:
            # 理论上不会走到这里，因为get_package_manager只返回uv
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            if result.returncode == 0:
                console.print("✅ 依赖安装成功", style="green")
                console.print("  ")
                console.print("启动项目运行命令：", style="green")
                console.print("    yoapi run")
                return 0
            else:
                console.print("❌ 依赖安装失败", style="red")
                return 1
        except Exception as e:
            console.print(f"❌ 安装依赖时出错: {e}", style="red")
            return 1
    
    def ensure_venv_activated(self) -> bool:
        """确保虚拟环境已激活"""
        # 检查是否在虚拟环境目录中
        python_executable = Path(sys.executable)
        
        # 检查是否在虚拟环境目录中
        if self.venv_dir.exists() and python_executable.is_relative_to(self.venv_dir):
            return True
        
        # 检查传统的虚拟环境标志
        if (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
            return True
        
        # 检查VIRTUAL_ENV环境变量
        if os.environ.get('VIRTUAL_ENV'):
            return True
        
        # 检查是否存在虚拟环境目录
        if self.venv_dir.exists():
            # 提供正确的激活命令
            if os.name == 'nt':  # Windows
                activate_cmd = ".venv\\Scripts\\activate"
                console.print("⚠️  检测到虚拟环境但未激活，请手动激活:", style="yellow")
                console.print(f"    {activate_cmd}")
                console.print("或者使用: .\\.venv\\Scripts\\activate")
            else:  # Unix/Linux/Mac
                activate_cmd = "source .venv/bin/activate"
                console.print("⚠️  检测到虚拟环境但未激活，请手动激活:", style="yellow")
                console.print(f"    {activate_cmd}")
            
            return False
        
        console.print("❌ 未检测到虚拟环境，请先创建虚拟环境", style="red")
        console.print("使用: yoapi venv create", style="yellow")
        return False


# 创建全局venv命令实例
venv_cmd = VenvCommand()
