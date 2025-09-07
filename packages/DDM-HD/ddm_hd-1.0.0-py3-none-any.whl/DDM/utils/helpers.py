"""
工具函数模块
"""
import hashlib
import time
from typing import Union


def generate_sign(cdkey: str, project_secret: str, project_uuid: str, device_info: str, timestamp: Union[int, str]) -> str:
    """
    生成登录签名字符串
    
    Args:
        cdkey (str): 卡密
        project_secret (str): 项目密钥
        project_uuid (str): 项目UUID
        device_info (str): 设备信息
        timestamp (Union[int, str]): 时间戳
        
    Returns:
        str: 32位MD5加密字符串
    """
    # 按照指定顺序拼接字符串: 卡密+卡密项目密钥+卡密项目UUID+设备信息+时间戳
    raw_string = f"{cdkey}{project_secret}{project_uuid}{device_info}{timestamp}"
    # 进行MD5加密并返回32位字符串
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()


def generate_heartbeat_sign(cdkey: str, token: str, project_secret: str, project_uuid: str, 
                           device_info: str, timestamp: Union[int, str]) -> str:
    """
    生成心跳签名字符串
    
    Args:
        cdkey (str): 卡密
        token (str): 登录成功时返回的token
        project_secret (str): 项目密钥
        project_uuid (str): 项目UUID
        device_info (str): 设备信息
        timestamp (Union[int, str]): 时间戳
        
    Returns:
        str: 32位MD5加密字符串
    """
    # 按照指定顺序拼接字符串: 卡密+Token+项目加密密钥+项目UUID+设备信息+时间戳
    raw_string = f"{cdkey}{token}{project_secret}{project_uuid}{device_info}{timestamp}"
    # 进行MD5加密并返回32位字符串
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()


def get_timestamp(length: int = 13) -> str:
    """
    获取指定长度的时间戳
    
    Args:
        length (int): 时间戳长度，10位(秒)或13位(毫秒)
        
    Returns:
        str: 时间戳字符串
        
    Raises:
        ValueError: 当length不是10或13时抛出异常
    """
    if length == 10:
        return str(int(time.time()))
    elif length == 13:
        return str(int(time.time() * 1000))
    else:
        raise ValueError("时间戳长度必须是10位或13位")