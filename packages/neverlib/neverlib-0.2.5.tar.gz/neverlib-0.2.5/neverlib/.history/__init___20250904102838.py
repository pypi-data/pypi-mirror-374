'''
Author: 凌逆战 | Never
Date: 2025-08-22
Description: 
'''
# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/5/17
"""
neverlib - 音频处理和VAD工具集
"""
# 从pyproject.toml中读取版本号
__version__ = "0.1.2"  # 默认版本号

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
    pass  # 如果出错, 使用默认版本号


# from neverlib import vad  # 只导入vad子包, 减少内存
# 如果没有neverlib.utils会报错
from . import utils
from . import vad
from . import audio_aug
from . import filter
