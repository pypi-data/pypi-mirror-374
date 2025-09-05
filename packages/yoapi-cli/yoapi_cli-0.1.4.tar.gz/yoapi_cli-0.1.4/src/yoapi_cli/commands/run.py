"""
运行命令模块 - 负责 WaveYo-API 项目的启动和运行
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

# 创建控制台实例
console = Console()


class RunCommand:
    """运行命令处理类"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.venv_dir = self.project_root / ".venv"
    
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
        
        console.print("❌ 未检测到虚拟环境，请先创建并激活虚拟环境", style="red")
        console.print("使用 uv: uv venv .venv", style="yellow")
        console.print("使用 venv: python -m venv .venv", style="yellow")
        return False
    
    def check_uvicorn_available(self) -> bool:
        """检查uvicorn是否可用"""
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import uvicorn; print(uvicorn.__version__)"],
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def run_project(self, reload: bool = False, port: int = 8000) -> int:
        """
        运行WaveYo-API项目
        
        Args:
            reload: 是否启用热重载模式
            port: 服务端口号
            
        Returns:
            int: 退出代码
        """
        # 检查虚拟环境
        if not self.ensure_venv_activated():
            return 1
        
        # 检查uvicorn是否可用
        if not self.check_uvicorn_available():
            console.print("❌ uvicorn 不可用，请先安装依赖", style="red")
            console.print("使用 uv: uv pip install -r requirements.txt", style="yellow")
            console.print("使用 pip: pip install -r requirements.txt", style="yellow")
            return 1
        
        # 构建uvicorn命令
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:create_app",
            "--host", "0.0.0.0",
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
            console.print("🚀 启动服务（热重载模式）...", style="blue")
        else:
            console.print("🚀 启动服务...", style="blue")
        
        console.print(f"📡 服务地址: http://localhost:{port}", style="green")
        console.print("📚 API文档: http://localhost:{port}/docs", style="green")
        console.print("⏹️  按 Ctrl+C 停止服务", style="yellow")
        
        try:
            # 运行uvicorn
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except KeyboardInterrupt:
            console.print("\n🛑 服务已停止", style="yellow")
            return 0
        except Exception as e:
            console.print(f"❌ 启动服务时出错: {e}", style="red")
            return 1


# 创建全局运行命令实例
run_cmd = RunCommand()
