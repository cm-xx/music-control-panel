import sys
from cx_Freeze import setup, Executable

# 依赖包
build_exe_options = {
    "packages": ["PySide6", "win32api", "win32gui", "win32con", "comtypes", "pycaw"],
    "includes": ["json", "os"],
    "include_files": ["icon.ico"],  # 包含图标文件
    "excludes": []
}

# 目标文件
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="音乐控制面板",  # 这里可以修改程序名称
    version="1.0",
    description="音乐播放控制工具",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            icon="icon.ico",  # 程序图标
            target_name="音乐控制面板.exe"  # 这里可以修改生成的exe文件名
        )
    ]
) 