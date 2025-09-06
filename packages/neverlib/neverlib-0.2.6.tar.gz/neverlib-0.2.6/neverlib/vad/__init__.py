# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/5/17
"""
节省路径
from neverlib.vad import EnergyVad_C
如果没有用户必须完整路径
from neverlib.vad.VAD_Energy import EnergyVad_C
"""
from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=["PreProcess", "VAD_Energy", "VAD_funasr", "VAD_Silero", "VAD_statistics", "VAD_vadlib", "VAD_WebRTC", "VAD_whisper", "utils"],
    submod_attrs={
        "VAD_Energy": ["EnergyVad_C"],
        "VAD_funasr": ["FunASR_VAD_C"],
        "VAD_Silero": ["Silero_VAD_C"],
        "VAD_statistics": ["Statistics_VAD"],
        "VAD_vadlib": ["Vadlib_C"],
        "VAD_WebRTC": ["WebRTC_VAD_C"],
        "VAD_whisper": ["Whisper_VAD_C"],
        "utils": ["from_vadArray_to_vadEndpoint", "vad2nad"],
    },
)
