'''
Author: 凌逆战 | Never
Date: 2025-03-17 19:23:33
Description: 
'''
"""
节省路径
from neverlib.filter import common
如果没有用户必须完整路径
from neverlib.filter.common import *
"""
from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=["common", "core", "biquad"],
    submod_attrs={
        "common": ["HPFilter", "LPFilter", "HPFilter_torch"],
    },
)
