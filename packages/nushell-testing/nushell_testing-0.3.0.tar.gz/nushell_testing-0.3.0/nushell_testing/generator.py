# test_data_generator.py
import os
import sys
import shutil
import tempfile
import random
import string
import platform
from pathlib import Path
import json
import subprocess
import time
import gzip
import zipfile
import tarfile

class TestDataGenerator:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path(tempfile.mkdtemp(prefix="nushell_test_"))
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.created_paths = []
        
    def cleanup(self):
        """清理所有生成的测试数据"""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)
            
    def create_mock_nu_exe(self, behavior="default", exit_code=0):
        """
        创建模拟的 nu.exe 文件
        behavior: 
            'default' - 基本功能
            'echo' - 回显所有参数
            'slow' - 模拟慢速启动
            'error' - 模拟错误输出
            'config' - 模拟配置加载
        """
        exe_path = self.data_dir / "nu.exe"
        
        if platform.system() == "Windows":
            # Windows 批处理文件
            content = f"""@echo off
setlocal

rem 模拟行为
if "{behavior}"=="echo" (
    echo Arguments: %*
    exit /b {exit_code}
)

if "{behavior}"=="slow" (
    ping 127.0.0.1 -n 3 > nul
    exit /b {exit_code}
)

if "{behavior}"=="error" (
    echo Error: Something went wrong 1>&2
    exit /b {exit_code}
)

if "{behavior}"=="config" (
    if "%~1"=="--config" (
        if exist "%~2" (
            echo Loaded config: %~2
        ) else (
            echo Config not found: %~2 1>&2
            exit /b 1
        )
    )
    exit /b {exit_code}
)

rem 默认行为
echo Nushell mock executable
exit /b {exit_code}
"""
            exe_path.write_text(content, encoding="utf-8")
        else:
            # Unix shell 脚本
            content = f"""#!/bin/bash

# 模拟行为
if [ "{behavior}" = "echo" ]; then
    echo "Arguments: $@"
    exit {exit_code}
fi

if [ "{behavior}" = "slow" ]; then
    sleep 2
    exit {exit_code}
fi

if [ "{behavior}" = "error" ]; then
    echo "Error: Something went wrong" >&2
    exit {exit_code}
fi

if [ "{behavior}" = "config" ]; then
    if [ "$1" = "--config" ]; then
        if [ -f "$2" ]; then
            echo "Loaded config: $2"
        else
            echo "Config not found: $2" >&2
            exit 1
        fi
    fi
    exit {exit_code}
fi

# 默认行为
echo "Nushell mock executable"
exit {exit_code}
"""
            exe_path.write_text(content, encoding="utf-8")
            exe_path.chmod(0o755)  # 添加执行权限
        
        self.created_paths.append(exe_path)
        return exe_path

    def create_complex_directory_structure(self, root_dir=None, depth=3, files_per_dir=5):
        """创建复杂的目录结构用于测试"""
        root = root_dir or self.base_dir / "test_data"
        root.mkdir(exist_ok=True)
        
        def create_dir(current, current_depth):
            if current_depth == 0:
                return
                
            # 创建子目录
            for i in range(random.randint(1, 3)):
                dir_name = f"dir_{current_depth}_{i}"
                if random.random() > 0.7:
                    dir_name += " with spaces"
                if random.random() > 0.8:
                    dir_name += "!@#$%^&()"
                    
                new_dir = current / dir_name
                new_dir.mkdir(exist_ok=True)
                self.created_paths.append(new_dir)
                
                # 在当前目录创建文件
                for j in range(files_per_dir):
                    self.create_random_file(current)
                
                # 递归创建子目录
                create_dir(new_dir, current_depth - 1)
        
        create_dir(root, depth)
        return root

    def create_random_file(self, directory, size_kb=1, extension=None):
        """创建随机内容的文件"""
        if not directory.exists():
            directory.mkdir(parents=True)
            
        ext = extension or random.choice(["txt", "csv", "log", "json", "xml", "bin"])
        filename = f"file_{random.randint(1000,9999)}.{ext}"
        if random.random() > 0.8:
            filename = f"file with spaces {random.randint(1000,9999)}.{ext}"
        if random.random() > 0.9:
            filename = f"file!@#$%^{random.randint(1000,9999)}.{ext}"
            
        file_path = directory / filename
        
        # 生成随机内容
        content = ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation + ' \n\t',
            k=size_kb * 1024
        ))
        
        file_path.write_text(content, encoding="utf-8")
        self.created_paths.append(file_path)
        return file_path

    def create_large_file(self, directory, size_mb=10):
        """创建大文件用于性能测试"""
        file_path = directory / f"large_file_{size_mb}MB.dat"
        
        chunk_size = 1024 * 1024  # 1MB
        with open(file_path, 'wb') as f:
            for _ in range(size_mb):
                f.write(os.urandom(chunk_size))
        
        self.created_paths.append(file_path)
        return file_path

    def create_config_file(self, content=None):
        """创建配置文件"""
        config_dir = self.base_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        if content is None:
            content = {
                "shell": {
                    "prompt": "nushell> ",
                    "history_size": 1000
                },
                "files": {
                    "max_open": 50
                }
            }
        
        config_path = config_dir / "config.nu"
        
        if isinstance(content, dict):
            config_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
        else:
            config_path.write_text(str(content), encoding="utf-8")
            
        self.created_paths.append(config_path)
        return config_path

    def create_environment_file(self, content=None):
        """创建环境变量文件"""
        env_dir = self.base_dir / "env"
        env_dir.mkdir(exist_ok=True)
        
        if content is None:
            content = {
                "PATH": "/usr/bin:/bin",
                "HOME": "/home/user",
                "LANG": "en_US.UTF-8"
            }
        
        env_path = env_dir / "env.nu"
        
        if isinstance(content, dict):
            env_content = "\n".join([f"let-env {k} = '{v}';" for k, v in content.items()])
            env_path.write_text(env_content, encoding="utf-8")
        else:
            env_path.write_text(str(content), encoding="utf-8")
            
        self.created_paths.append(env_path)
        return env_path

    def create_compressed_file(self, directory, format="zip"):
        """创建压缩文件"""
        # 先创建一些文件用于压缩
        temp_dir = directory / "compress_src"
        temp_dir.mkdir(exist_ok=True)
        for _ in range(5):
            self.create_random_file(temp_dir)
        
        if format == "zip":
            zip_path = directory / "archive.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in temp_dir.iterdir():
                    zipf.write(file, file.name)
            self.created_paths.append(zip_path)
            return zip_path
            
        elif format == "gzip":
            gz_path = directory / "archive.tar.gz"
            with tarfile.open(gz_path, "w:gz") as tar:
                for file in temp_dir.iterdir():
                    tar.add(file, arcname=file.name)
            self.created_paths.append(gz_path)
            return gz_path
            
        elif format == "tar":
            tar_path = directory / "archive.tar"
            with tarfile.open(tar_path, "w") as tar:
                for file in temp_dir.iterdir():
                    tar.add(file, arcname=file.name)
            self.created_paths.append(tar_path)
            return tar_path

    def create_symlink(self, target, link_name):
        """创建符号链接（如果平台支持）"""
        if hasattr(os, "symlink"):
            os.symlink(target, link_name)
            self.created_paths.append(Path(link_name))
            return Path(link_name)
        return None

    def create_hardlink(self, target, link_name):
        """创建硬链接"""
        if hasattr(os, "link"):
            os.link(target, link_name)
            self.created_paths.append(Path(link_name))
            return Path(link_name)
        return None

    def set_environment_variables(self, env_vars):
        """设置环境变量"""
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        return env_vars

    def measure_performance(self, command, iterations=10):
        """测量命令执行性能"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "total": sum(times)
        }

    def generate_test_arguments(self, count=100):
        """生成测试参数列表"""
        arguments = []
        
        # 基本参数
        basic_args = ["-c", "--version", "--help", "--stdin", "--config", "test.conf"]
        
        # 路径参数
        path_args = [
            "C:\\Program Files",
            "/usr/local/bin",
            "~/Documents",
            "path with spaces",
            "path!@#$%^&()",
            "中文路径",
            "🚀/特殊/路径"
        ]
        
        # 命令参数
        command_args = [
            "ls",
            "ls | where size > 1mb",
            "echo 'Hello, World!'",
            "open data.csv | where amount > 100",
            "ps | where cpu > 10",
            "git status",
            "docker ps -a"
        ]
        
        # 组合参数
        for _ in range(count):
            arg_set = []
            # 随机添加基本参数
            if random.random() > 0.3:
                arg_set.append(random.choice(basic_args))
                
            # 随机添加路径参数
            if random.random() > 0.4:
                arg_set.append(random.choice(path_args))
                
            # 随机添加命令参数
            if random.random() > 0.5:
                arg_set.append(random.choice(command_args))
                
            # 添加一些随机字符串
            if random.random() > 0.6:
                arg_set.append(''.join(random.choices(string.printable, k=random.randint(5, 50))))
                
            arguments.append(arg_set)
            
        return arguments

    def create_test_repository(self):
        """创建包含所有测试数据的完整仓库"""
        repo = {
            "nu_exe": self.create_mock_nu_exe(),
            "data_dir": self.create_complex_directory_structure(),
            "config_file": self.create_config_file(),
            "env_file": self.create_environment_file(),
            "large_file": self.create_large_file(self.base_dir, 5),
            "zip_file": self.create_compressed_file(self.base_dir, "zip"),
            "gzip_file": self.create_compressed_file(self.base_dir, "gzip")
        }
        
        # 尝试创建符号链接
        symlink = self.create_symlink(
            repo["data_dir"] / "dir_3_0", 
            self.base_dir / "symlink_dir"
        )
        if symlink:
            repo["symlink"] = symlink
            
        return repo


# 示例用法
if __name__ == "__main__":
    print("Nushell 测试数据生成器")
    generator = TestDataGenerator()
    
    try:
        print(f"创建测试环境于: {generator.base_dir}")
        
        # 创建模拟的 nu.exe
        nu_exe = generator.create_mock_nu_exe(behavior="echo")
        print(f"创建模拟 nu.exe: {nu_exe}")
        
        # 创建复杂目录结构
        data_dir = generator.create_complex_directory_structure()
        print(f"创建测试数据目录: {data_dir}")
        
        # 创建配置文件
        config_file = generator.create_config_file()
        print(f"创建配置文件: {config_file}")
        
        # 创建环境文件
        env_file = generator.create_environment_file()
        print(f"创建环境文件: {env_file}")
        
        # 创建大文件
        large_file = generator.create_large_file(generator.base_dir, 2)
        print(f"创建大文件: {large_file} (2MB)")
        
        # 创建压缩文件
        zip_file = generator.create_compressed_file(generator.base_dir)
        print(f"创建ZIP文件: {zip_file}")
        
        # 测试参数生成
        test_args = generator.generate_test_arguments(5)
        print("\n生成的测试参数示例:")
        for i, args in enumerate(test_args, 1):
            print(f"{i}. {args}")
        
        # 测试性能测量
        print("\n性能测试示例:")
        perf = generator.measure_performance([str(nu_exe), "--version"])
        print(f"执行时间: min={perf['min']:.4f}s, max={perf['max']:.4f}s, avg={perf['avg']:.4f}s")
        
        print("\n测试数据生成完成。")
        print(f"所有测试数据位于: {generator.base_dir}")
        print("清理时将删除此目录及其内容。")
        
    finally:
        # 在实际测试中，你可能不想立即清理
        # generator.cleanup()
        pass