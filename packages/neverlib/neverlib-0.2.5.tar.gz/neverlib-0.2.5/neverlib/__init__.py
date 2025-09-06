'''
Author: 凌逆战 | Never
Date: 2025-08-22
Description: neverlib - 音频处理和VAD工具集
'''
try:
    import re
    import pathlib
    
    # 获取pyproject.toml的路径
    _pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    
    # 读取版本号
    if _pyproject_path.exists():
        with open(_pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 使用正则表达式匹配版本号
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                __version__ = version_match.group(1)
except Exception:
    __version__ = "0.1.2"  # 如果出错, 使用默认版本号


# 懒加载子包，减少初始导入开销
from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=["utils", "vad", "audio_aug", "filter", "data_analyze"],
)
