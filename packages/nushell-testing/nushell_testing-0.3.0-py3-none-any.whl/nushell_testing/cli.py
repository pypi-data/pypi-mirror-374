import os
import sys
import subprocess
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil

def main():
    exe_path = Path(__file__).parent / 'data' / 'nu.exe'
    if not exe_path.exists():
        print(f"Error: {exe_path} not found!")
        sys.exit(1)
    result = subprocess.run([str(exe_path)] + sys.argv[1:])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

# ======================== TEST CASES ========================
class TestNushellLauncher(unittest.TestCase):
    def setUp(self):
        # 创建临时目录结构
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # 创建模拟的包目录结构
        self.package_dir = Path(self.test_dir) / "package"
        self.data_dir = self.package_dir / "data"
        self.data_dir.mkdir(parents=True)
        
        # 创建测试用的 nu.exe
        self.real_exe = self.data_dir / "nu.exe"
        self.real_exe.touch()
        
        # 保存原始 sys.argv
        self.original_argv = sys.argv.copy()
        
    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        sys.argv = self.original_argv

    # ----- 核心功能测试 -----
    @patch("subprocess.run")
    def test_normal_execution(self, mock_run):
        """测试正常执行路径"""
        sys.argv = ["launcher.py", "--version"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit") as mock_exit:
            main()
            
        mock_run.assert_called_once_with(
            [str(self.real_exe), "--version"],
            check=False
        )
        mock_exit.assert_called_once_with(0)

    @patch("subprocess.run")
    def test_argument_passing(self, mock_run):
        """测试参数传递功能"""
        sys.argv = ["launcher.py", "-c", "ls | length", "C:\\"]
        mock_run.return_value = MagicMock(returncode=42)
        
        with patch("sys.exit") as mock_exit:
            main()
            
        mock_run.assert_called_once_with(
            [str(self.real_exe), "-c", "ls | length", "C:\\"],
            check=False
        )
        mock_exit.assert_called_once_with(42)

    # ----- 错误处理测试 -----
    def test_missing_executable(self):
        """测试缺少可执行文件的情况"""
        self.real_exe.unlink()
        
        with patch("sys.exit") as mock_exit, \
             patch("builtins.print") as mock_print:
            main()
            
        mock_print.assert_called_once_with(
            f"Error: {self.real_exe} not found!"
        )
        mock_exit.assert_called_once_with(1)

    @patch("subprocess.run")
    def test_non_zero_exit_code(self, mock_run):
        """测试非零退出码处理"""
        sys.argv = ["launcher.py"]
        mock_run.return_value = MagicMock(returncode=127)
        
        with patch("sys.exit") as mock_exit:
            main()
            
        mock_exit.assert_called_once_with(127)

    # ----- 路径处理测试 -----
    @patch("subprocess.run")
    def test_spaces_in_path(self, mock_run):
        """测试路径中包含空格的情况"""
        space_dir = self.data_dir / "dir with spaces"
        space_dir.mkdir()
        space_exe = space_dir / "nu.exe"
        space_exe.touch()
        
        # 修改主函数中的路径
        with patch("__main__.Path") as mock_path:
            mock_path.return_value.parent = self.package_dir
            mock_path.return_value.__truediv__.side_effect = lambda x: space_dir / x if x == "data" else space_exe
            
            sys.argv = ["launcher.py"]
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch("sys.exit"):
                main()
                
        mock_run.assert_called_once_with([str(space_exe)], check=False)

    @patch("subprocess.run")
    def test_special_characters_in_path(self, mock_run):
        """测试路径中包含特殊字符的情况"""
        special_dir = self.data_dir / "dir!@#$%^&()"
        special_dir.mkdir()
        special_exe = special_dir / "nu.exe"
        special_exe.touch()
        
        with patch("__main__.Path") as mock_path:
            mock_path.return_value.parent = self.package_dir
            mock_path.return_value.__truediv__.side_effect = lambda x: special_dir / x if x == "data" else special_exe
            
            sys.argv = ["launcher.py"]
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch("sys.exit"):
                main()
                
        mock_run.assert_called_once_with([str(special_exe)], check=False)

    # ----- 环境测试 -----
    @patch("subprocess.run")
    def test_current_working_directory(self, mock_run):
        """测试工作目录是否正确"""
        new_cwd = self.package_dir / "subdir"
        new_cwd.mkdir()
        os.chdir(new_cwd)
        
        sys.argv = ["launcher.py"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        mock_run.assert_called_once_with([str(self.real_exe)], check=False)

    @patch("subprocess.run")
    def test_unicode_arguments(self, mock_run):
        """测试Unicode参数支持"""
        sys.argv = ["launcher.py", "测试", "🚀", "©"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        mock_run.assert_called_once_with(
            [str(self.real_exe), "测试", "🚀", "©"],
            check=False
        )

    # ----- 边缘情况测试 -----
    @patch("subprocess.run")
    def test_no_arguments(self, mock_run):
        """测试无命令行参数的情况"""
        sys.argv = ["launcher.py"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        mock_run.assert_called_once_with([str(self.real_exe)], check=False)

    @patch("subprocess.run")
    def test_large_number_of_arguments(self, mock_run):
        """测试大量参数的情况"""
        sys.argv = ["launcher.py"] + [f"arg{i}" for i in range(1000)]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        self.assertEqual(len(mock_run.call_args[0][0]), 1001)

    @patch("subprocess.run")
    def test_empty_arguments(self, mock_run):
        """测试空字符串参数"""
        sys.argv = ["launcher.py", "", "''", '""']
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        mock_run.assert_called_once_with(
            [str(self.real_exe), "", "''", '""'],
            check=False
        )

    # ----- 子进程行为测试 -----
    @patch("subprocess.run")
    def test_subprocess_failure(self, mock_run):
        """测试子进程执行失败"""
        sys.argv = ["launcher.py"]
        mock_run.side_effect = OSError("Execution failed")
        
        with patch("sys.exit") as mock_exit:
            main()
            
        mock_exit.assert_called_once_with(1)

    @patch("subprocess.run")
    def test_check_false_behavior(self, mock_run):
        """测试check=False时的行为"""
        sys.argv = ["launcher.py"]
        mock_run.return_value = MagicMock(returncode=255)
        
        with patch("sys.exit") as mock_exit:
            main()
            
        mock_exit.assert_called_once_with(255)
        mock_run.assert_called_once_with([str(self.real_exe)], check=False)

    # ----- 安全测试 -----
    @patch("subprocess.run")
    def test_path_traversal_attempt(self, mock_run):
        """测试路径遍历攻击尝试"""
        malicious_path = self.package_dir / ".." / "sensitive.txt"
        
        sys.argv = ["launcher.py", str(malicious_path)]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        # 验证路径没有被规范化（应由nu.exe处理）
        self.assertIn(str(malicious_path), mock_run.call_args[0][0])

    @patch("subprocess.run")
    def test_injection_attempt(self, mock_run):
        """测试命令注入尝试"""
        sys.argv = ["launcher.py", "; rm -rf /"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        # 验证参数作为单个参数传递
        self.assertEqual(mock_run.call_args[0][0][1], "; rm -rf /")

    # ----- 跨平台测试 -----
    @patch("subprocess.run")
    def test_windows_path_handling(self, mock_run):
        """测试Windows路径处理"""
        with patch("os.name", "nt"):
            sys.argv = ["launcher.py", "C:\\Program Files"]
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch("sys.exit"):
                main()
                
        mock_run.assert_called_once_with(
            [str(self.real_exe), "C:\\Program Files"],
            check=False
        )

    @patch("subprocess.run")
    def test_posix_path_handling(self, mock_run):
        """测试POSIX路径处理"""
        with patch("os.name", "posix"):
            sys.argv = ["launcher.py", "/usr/bin"]
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch("sys.exit"):
                main()
                
        mock_run.assert_called_once_with(
            [str(self.real_exe), "/usr/bin"],
            check=False
        )

    # ----- 性能测试 -----
    @patch("subprocess.run")
    def test_execution_time(self, mock_run):
        """测试启动时间性能"""
        import time
        sys.argv = ["launcher.py", "--version"]
        mock_run.return_value = MagicMock(returncode=0)
        
        start_time = time.time()
        with patch("sys.exit"):
            main()
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 2.0)  # 应在2秒内完成

    # ----- 文件系统测试 -----
    def test_symlink_handling(self):
        """测试符号链接处理"""
        if hasattr(os, "symlink"):  # 跳过不支持符号链接的平台
            link_dir = self.package_dir / "linked_data"
            os.symlink(self.data_dir, link_dir)
            
            # 修改主函数中的路径
            with patch("__main__.Path") as mock_path:
                mock_path.return_value.parent = self.package_dir
                mock_path.return_value.__truediv__.side_effect = lambda x: link_dir / x if x == "data" else link_dir / "nu.exe"
                
                # 应该能解析符号链接
                self.assertTrue(Path(link_dir / "nu.exe").exists())
                
                sys.argv = ["launcher.py"]
                with patch("subprocess.run") as mock_run, \
                     patch("sys.exit"):
                    mock_run.return_value = MagicMock(returncode=0)
                    main()
                    
                mock_run.assert_called_once_with([str(link_dir / "nu.exe")], check=False)

    # ----- 权限测试 -----
    @unittest.skipUnless(os.name == 'posix', "Requires POSIX permissions")
    def test_execution_permission(self):
        """测试可执行权限处理"""
        self.real_exe.chmod(0o644)  # 移除执行权限
        
        with patch("sys.exit") as mock_exit, \
             patch("builtins.print") as mock_print:
            main()
            
        mock_print.assert_called_once_with(
            f"Error: {self.real_exe} not found!"
        )
        mock_exit.assert_called_once_with(1)

    # ----- 配置测试 -----
    @patch("subprocess.run")
    def test_config_file_loading(self, mock_run):
        """测试配置加载行为"""
        config_file = self.package_dir / "config.nu"
        config_file.write_text("config content")
        
        sys.argv = ["launcher.py", "--config", str(config_file)]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch("sys.exit"):
            main()
            
        mock_run.assert_called_once_with(
            [str(self.real_exe), "--config", str(config_file)],
            check=False
        )

    # ----- 环境变量测试 -----
    @patch("subprocess.run")
    def test_environment_passthrough(self, mock_run):
        """测试环境变量传递"""
        sys.argv = ["launcher.py"]
        mock_run.return_value = MagicMock(returncode=0)
        
        with patch.dict("os.environ", {"TEST_VAR": "value123"}, clear=True), \
             patch("sys.exit"):
            main()
            
        # 验证环境变量传递给子进程
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[1]["env"]["TEST_VAR"], "value123")

    # ----- 退出码测试 -----
    @patch("subprocess.run")
    def test_exit_code_range(self, mock_run):
        """测试各种退出码处理"""
        for code in [0, 1, 127, 255]:
            with self.subTest(exit_code=code):
                sys.argv = ["launcher.py"]
                mock_run.reset_mock()
                mock_run.return_value = MagicMock(returncode=code)
                
                with patch("sys.exit") as mock_exit:
                    main()
                    
                mock_exit.assert_called_once_with(code)

    # ----- 日志测试 -----
    @patch("subprocess.run")
    def test_error_logging(self, mock_run):
        """测试错误日志输出"""
        sys.argv = ["launcher.py"]
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=[str(self.real_exe)],
            output=b"Error output",
            stderr=b"Error message"
        )
        
        with patch("sys.exit") as mock_exit, \
             patch("builtins.print") as mock_print:
            main()
            
        mock_exit.assert_called_once_with(1)
        self.assertTrue(mock_print.call_count >= 1)

if __name__ == "__main__":
    unittest.main()