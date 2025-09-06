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
    
    def detect_virtual_env(self) -> Optional[Path]:
        """检测并返回虚拟环境的Python可执行文件路径"""
        # 检查常见的虚拟环境目录
        venv_dirs = [".venv", "venv", "env"]
        
        for venv_dir_name in venv_dirs:
            venv_dir = self.project_root / venv_dir_name
            if venv_dir.exists():
                # 检查不同平台的Python可执行文件路径
                python_paths = []
                if os.name == 'nt':  # Windows
                    python_paths.append(venv_dir / "Scripts" / "python.exe")
                    python_paths.append(venv_dir / "Scripts" / "python")
                else:  # Unix/Linux/Mac
                    python_paths.append(venv_dir / "bin" / "python")
                    python_paths.append(venv_dir / "bin" / "python3")
                
                for python_path in python_paths:
                    if python_path.exists():
                        return python_path
        
        # 检查是否已经在虚拟环境中
        python_executable = Path(sys.executable)
        for venv_dir_name in venv_dirs:
            venv_dir = self.project_root / venv_dir_name
            if venv_dir.exists() and python_executable.is_relative_to(venv_dir):
                return python_executable
        
        # 检查传统的虚拟环境标志
        if (hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
            return python_executable
        
        # 检查VIRTUAL_ENV环境变量
        if os.environ.get('VIRTUAL_ENV'):
            venv_path = Path(os.environ['VIRTUAL_ENV'])
            if os.name == 'nt':
                return venv_path / "Scripts" / "python.exe"
            else:
                return venv_path / "bin" / "python"
        
        return None
    
    def ensure_venv_activated(self) -> Optional[Path]:
        """确保虚拟环境已激活，返回虚拟环境的Python路径"""
        venv_python = self.detect_virtual_env()
        
        if venv_python:
            # 检查是否已经在使用虚拟环境的Python
            current_python = Path(sys.executable)
            if current_python == venv_python:
                console.print("✅ 虚拟环境已激活", style="green")
                return venv_python
            else:
                console.print(f"⚠️  检测到虚拟环境，将使用: {venv_python}", style="yellow")
                return venv_python
        else:
            # 检查是否存在虚拟环境目录但无法找到Python
            venv_dirs = [".venv", "venv", "env"]
            for venv_dir_name in venv_dirs:
                venv_dir = self.project_root / venv_dir_name
                if venv_dir.exists():
                    console.print("❌ 检测到虚拟环境目录但无法找到Python可执行文件", style="red")
                    console.print("请重新创建虚拟环境:", style="yellow")
                    console.print("使用 uv: uv venv .venv", style="yellow")
                    return None
            
            console.print("❌ 未检测到虚拟环境", style="red")
            console.print("请先创建虚拟环境:", style="yellow")
            console.print("使用 uv: uv venv .venv", style="yellow")
            return None
    
    def check_uvicorn_available(self, python_executable: Optional[Path] = None) -> bool:
        """检查uvicorn是否可用"""
        python_cmd = python_executable or Path(sys.executable)
        try:
            result = subprocess.run(
                [str(python_cmd), "-c", "import uvicorn; print(uvicorn.__version__)"],
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
        # 检测虚拟环境并获取Python路径
        venv_python = self.ensure_venv_activated()
        if not venv_python:
            return 1
        
        # 检查uvicorn是否在虚拟环境中可用
        if not self.check_uvicorn_available(venv_python):
            console.print("❌ uvicorn 在虚拟环境中不可用，请先安装依赖", style="red")
            console.print("使用 uv: uv pip install -r requirements.txt", style="yellow")
            return 1
        
        # 构建uvicorn命令，使用虚拟环境的Python
        cmd = [
            str(venv_python), "-m", "uvicorn",
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
        console.print(f"📚 API文档: http://localhost:{port}/docs", style="green")
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
