"""
下载工具相关
"""
import hashlib
import os
import sys
from pathlib import Path


def get_root_path() -> Path:
    """动态获取项目根目录（兼容开发/Nuitka/PyInstaller单双文件模式）"""
    # 环境变量覆盖
    if env_root := os.getenv("APP_ROOT"):
        return Path(env_root).resolve()

    is_pyinstaller = getattr(sys, 'frozen', False) or getattr(sys, '_MEIPASS', False)
    is_nuitka = "__compiled__" in globals()

    base_path = None
    executable_path = Path(sys.executable).resolve()
    if is_pyinstaller:
        # PyInstaller打包时会设置sys.frozen=True和sys._MEIPASS=True,此时使用Path(sys.executable)和Path(sys.argv[0])效果相同
        # sys.argv[0] 是 sys 模块提供的命令行参数列表的第一个元素，表示被执行的脚本名称.如果程序启动时显式传递了额外参数，sys.argv[0] 会被替换为第一个参数,所以优先使用sys.executable更稳定
        base_path = executable_path.parent
    elif is_nuitka:
        base_path = executable_path.parent
    else:
        # 开发环境检测,获取所有父级目录,判断其下是否包含root_markers任一文件,包含则认为是项目根目录
        current_path = Path(__file__).resolve()
        root_markers = [
            'requirements.txt', 'deploy.py', 'setup.py', '.git', '.svn', '.gitignore', 'app', 'main.py'
        ]
        max_depth = 10
        for i, parent in enumerate(current_path.parents):
            if i > max_depth:
                raise RuntimeError(f"开发环境查找目录时超过最大搜索层级:{max_depth}")
            if any((parent / marker).resolve().exists() for marker in root_markers):
                base_path = parent.resolve()
                break

    # 判断路径是否存在
    if not base_path or not base_path.exists():
        raise RuntimeError("未找到项目根目录")
    return base_path


def count_files(folder_path, extension, recursive=True, pattern_fn=None):
    """统计目录下指定格式的文件数量（支持递归、自定义匹配）"""
    path = Path(folder_path)
    if not path.is_dir():
        return 0

    # 默认匹配规则：后缀严格等于 extension（支持多扩展名）
    pattern_fn = pattern_fn or (lambda f, ext: f.suffix == ext)
    pattern = f"**/*{extension}" if recursive else f"*{extension}"

    try:
        files = path.rglob(pattern) if recursive else path.glob(pattern)
        return sum(1 for file in files if file.is_file() and pattern_fn(file, extension))
    except PermissionError:
        return 0  # 或抛出警告


def calculate_file_md5(file_path: str) -> str:
    """分块计算文件MD5，避免内存溢出"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# 使用示例
if __name__ == "__main__":
    root_path = get_root_path()
    print("root_path:", root_path)

    files_count = count_files(r"D:\Downloads\baidu_machine", ".jpg", False)
    print("files count:", files_count)
