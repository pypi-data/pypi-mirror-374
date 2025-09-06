# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/5/17
"""
音频增强模块
"""
from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=["audio_aug"],
)