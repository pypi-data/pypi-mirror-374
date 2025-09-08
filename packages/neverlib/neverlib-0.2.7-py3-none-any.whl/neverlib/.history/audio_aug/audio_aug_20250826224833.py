# -*- coding:utf-8 -*-
# Author:凌逆战 | Never
# Date: 2024/9/27
"""

"""
import random
import numpy as np
import soundfile as sf
from scipy import signal
from neverlib.utils import EPS
from neverlib.filter import HPFilter


def volume_norm(wav):
    """
    音量归一化
    :param wav: (T,)
    :return: (T,)
    """
    wav = wav / (np.max(np.abs(wav)) + 1e-8)
    return wav


def add_reverb(wav, rir, ratio=1, mode="same"):
    """添加混响,
    Args:
        wav: [T, channel]
        rir: [T, channel]
        ratio:  0-1
        mode: "same" for SE or "full" for kws
    """
    if random.random() < ratio:
        wav = signal.fftconvolve(wav, rir, mode=mode)  # (28671, 3)
        # note: 建议过完添加混响后再进行归一化, 否则可能会出现溢出
        # 防止削波
        if np.max(np.abs(wav)) > 1:
            scale_factor = 1 / np.max(np.abs(wav))
            wav *= scale_factor
    return wav


def snr_aug_changeNoise(clean, noise, target_snr, hp=False, sr=16000, order=4, cutoff=100):
    """ 
    保持语音不变, 改变噪声的幅度
    HP: 高通滤波, 如果你的数据工频干扰较高, 建议设置为True, 否则snr会不准
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    noise_scale = np.sqrt(clean_power / (noise_power * 10 ** (target_snr / 10) + EPS))
    noisy = clean + noise_scale * noise
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, clean


def snr_aug_changeClean(clean, noise, target_snr, clip_check=True, hp=False, sr=16000, order=4, cutoff=100):
    """ 
    保持噪声不变，改变纯净语音的幅度以达到目标信噪比
    snr = 10 * log10(k*signal_power/ noise_power)
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    # 计算纯净信号需要的幅度因子
    clean_scale = np.sqrt(noise_power * 10 ** (target_snr / 10) / (clean_power + EPS))
    noisy = clean * clean_scale + noise
    # 防止削波
    if clip_check:
        if np.max(np.abs(noisy)) > 1:
            scale_factor = 1 / np.max(np.abs(noisy))
            noisy *= scale_factor
            clean *= (scale_factor * clean_scale)
    return noisy, clean


def snr_diff_changeNoise(clean, noise, target_snr, hp=False, sr=16000, order=4, cutoff=100):
    """ 
    保持语音不变, 改变噪声的幅度, 和snr_aug_changeNoise作用等效
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    source_snr = 10 * np.log10(clean_power / (noise_power + EPS) + EPS)
    noise_dB = source_snr - target_snr     # 噪声还差多少dB
    noise_gain = 10 ** (noise_dB / 20)
    noisy = clean + noise_gain * noise
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, clean


def snr_diff_changeClean(clean, noise, target_snr, clip_check=True, hp=False, sr=16000, order=4, cutoff=100):
    """ 
    保持噪声不变, 改变纯净语音的幅度, 和snr_aug_changeClean作用等效
    snr = 10 * log10(signal_power / k*noise_power) 
    """
    assert clean.shape == noise.shape, "clean and noise must have the same shape"
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    # 纯净语音功率, 噪声功率
    clean_power, noise_power = np.mean(clean_tmp ** 2), np.mean(noise_tmp ** 2)
    source_snr = 10 * np.log10(clean_power / (noise_power + EPS) + EPS)
    clean_dB = target_snr - source_snr     # 纯净语音还差多少dB
    clean_gain = 10 ** (clean_dB / 20)
    noisy = clean_gain * clean + noise
    # 防止削波
    if clip_check:
        if np.max(np.abs(noisy)) > 1:
            scale_factor = 1 / np.max(np.abs(noisy))
            noisy *= scale_factor
            clean *= (scale_factor * clean_gain)
    return noisy, clean


def snr_aug_Interpolation(clean, noise, target_snr, hp=False, sr=16000, order=4, cutoff=100):
    """
    在已知clean_len<=noise_len的情况下
    将clean插入到noise中的snr aug方法
    Args:
        clean: 语音
        noise: 噪声
        snr: snr=random.uniform(*snr_range)
    """
    clean_len, noise_len = clean.shape[0], noise.shape[0]
    assert clean_len <= noise_len, f"clean_len must be less than noise_len."
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    noisy = noise.copy()
    index = random.randint(0, noise_len - clean_len)
    noise_tmp = noise_tmp[index:index + clean_len, :]
    # 这里必须把clip_check设置为False, 否则外面的noise和里面的不一致
    noisy_tmp, clean_tmp = snr_aug_changeClean(clean_tmp, noise_tmp, target_snr, clip_check=False, hp=False)
    noisy[index:index + clean_len, :] = noisy_tmp
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean *= scale_factor
    return noisy, clean_tmp

def get_snr_use_vad(wav, vad, sr=16000):
    # 通过vad获得语音原始的snr
    wav = HPFilter(wav, sr=sr, order=6, cutoff=100)
    vadstart, vadend = vad["start"], vad["end"]
    noise = np.concatenate([wav[:vadstart], wav[vadend:]], axis=0)
    speech_segment = wav[vadstart:vadend]

    # 计算信噪比
    # 统计语音段的均方功率谱
    P_speech_noise = np.mean(speech_segment ** 2)  # 语音+噪声功率
    # P_speech_noise = np.mean(wav ** 2)  # 如果用全局的, 会存在噪声功率过大的问题, 导致snr过低
    P_noise = np.mean(noise ** 2)  # 纯噪声功率

    # 计算净语音功率(确保非负)
    P_speech = max(P_speech_noise - P_noise, 1e-8)
    if P_noise < 1e-8:
        P_noise = 1e-8
    
    snr = 10 * np.log10(P_speech / P_noise) # 计算 SNR
    # snr保留小数点后一位
    return round(snr, 1)

def snr_aug_vad_Interpolation(clean, noise, target_snr, vad, hp=False, sr=16000, order=4, cutoff=100):
    """
    在已知clean_len<=noise_len的情况下, 将clean插入到noise中的snr aug方法,
    使用VAD信息, 精确地找到语音位置
    Args:
        clean: 语音
        noise: 噪声
        vad: {"start": xxx, "end": xxx}
    """
    clean_len, noise_len = clean.shape[0], noise.shape[0]
    assert clean_len <= noise_len, f"clean_len must be less than noise_len."
    clean_tmp, noise_tmp = clean.copy(), noise.copy()
    if hp:
        clean_tmp = HPFilter(clean_tmp, sr=sr, order=order, cutoff=cutoff)
        noise_tmp = HPFilter(noise_tmp, sr=sr, order=order, cutoff=cutoff)
    
    source_snr = get_snr_use_vad(clean_tmp, vad, sr=sr)
    assert source_snr > target_snr, f"source_snr must be greater than target_snr."
        clean_tmp = clean[vad_start:vad_end]
    noise_tmp = noise[vad_start:vad_end]
    
    noisy = noise.copy()
    index = random.randint(0, noise_len - clean_len)
    noise_tmp = noise_tmp[index:index + clean_len, :]
    # 这里必须把clip_check设置为False, 否则外面的noise和里面的不一致
    noisy_tmp, clean_tmp = snr_aug_changeClean(clean_tmp, noise_tmp, target_snr, clip_check=False, hp=False)
    noisy[index:index + clean_len, :] = noisy_tmp
    # 防止削波
    if np.max(np.abs(noisy)) > 1:
        scale_factor = 1 / np.max(np.abs(noisy))
        noisy *= scale_factor
        clean_tmp *= scale_factor
    return noisy, clean_tmp


def get_audio_segments(wav_len, audio_path_list, sr=16000):
    """
    从音频列表中随机拼接指定长度音频
    Args:
        wav_len: 需要返回的音频长度
        audio_path_list: 音频路径列表
        sr: 采样率
    Returns:返回指定长度的音频
    """
    audio_len = 0
    wav_list = []
    while audio_len < wav_len:
        audio_path = random.choice(audio_path_list)
        wav, wav_sr = sf.read(audio_path, always_2d=True, dtype='float32')
        assert wav_sr == sr, f"音频采样率是{wav_sr}, 期望{sr}"
        audio_len += len(wav)
        wav_list.append(wav)
    wav = np.concatenate(wav_list, axis=0)
    if len(wav) > wav_len:
        # 随机截取clean_len
        start = random.randint(0, len(wav) - wav_len)
        wav = wav[start:start + wav_len, :]
    return wav


def volume_aug(wav, range, rate, method="linmax"):
    """音量增强 """
    if random.random() < rate:
        target_level = random.uniform(range[0], range[1])
        if method == "dbrms":
            wav_rms = (wav ** 2).mean() ** 0.5
            scalar = 10 ** (target_level / 20) / (np.max(wav_rms) + EPS)
        elif method == "linmax":
            ipt_max = np.max(np.abs(wav))
            # wav/wav_max*target_level=target_level_wav
            # 处理后音频的 最大值就是target_level
            scalar = target_level / (ipt_max + EPS)
        else:
            raise ValueError("method must be 'dbrms' or 'linmax'")
        wav *= scalar
    return wav
