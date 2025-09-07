"""
设备信息工具模块，用于获取Windows平台的机器码
"""
import uuid
import platform
import hashlib
import subprocess
import re
from typing import Optional


def get_machine_code() -> str:
    """
    获取Windows平台的机器码
    
    Returns:
        str: 机器码字符串
    """
    try:
        # 获取主板序列号
        motherboard_serial = _get_motherboard_serial()
        
        # 获取CPU信息
        cpu_info = _get_cpu_info()
        
        # 获取硬盘序列号
        disk_serial = _get_disk_serial()
        
        # 获取MAC地址
        mac_address = _get_mac_address()
        
        # 组合所有硬件信息
        hardware_info = f"{motherboard_serial}{cpu_info}{disk_serial}{mac_address}"
        
        # 生成MD5哈希作为机器码
        machine_code = hashlib.md5(hardware_info.encode('utf-8')).hexdigest()
        
        return machine_code
    except Exception:
        # 如果获取硬件信息失败，则使用UUID方式
        return _get_fallback_machine_code()


def get_device_info() -> str:
    """
    获取设备信息，用于卡密验证
    
    Returns:
        str: 设备信息字符串
    """
    return get_machine_code()


def _get_motherboard_serial() -> str:
    """
    获取主板序列号
    
    Returns:
        str: 主板序列号
    """
    try:
        result = subprocess.run(
            ["wmic", "baseboard", "get", "serialnumber"],
            capture_output=True,
            text=True,
            check=True
        )
        # 提取序列号
        serial = re.search(r'SerialNumber\s*\n(.+)', result.stdout)
        if serial:
            return serial.group(1).strip()
        return ""
    except Exception:
        return ""


def _get_cpu_info() -> str:
    """
    获取CPU信息
    
    Returns:
        str: CPU信息
    """
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "ProcessorId"],
            capture_output=True,
            text=True,
            check=True
        )
        # 提取处理器ID
        processor_id = re.search(r'ProcessorId\s*\n(.+)', result.stdout)
        if processor_id:
            return processor_id.group(1).strip()
        return ""
    except Exception:
        return platform.processor()


def _get_disk_serial() -> str:
    """
    获取硬盘序列号
    
    Returns:
        str: 硬盘序列号
    """
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "serialnumber"],
            capture_output=True,
            text=True,
            check=True
        )
        # 提取序列号
        serial = re.search(r'SerialNumber\s*\n(.+)', result.stdout)
        if serial:
            return serial.group(1).strip()
        return ""
    except Exception:
        return ""


def _get_mac_address() -> str:
    """
    获取MAC地址
    
    Returns:
        str: MAC地址
    """
    try:
        mac = uuid.getnode()
        return ':'.join(['{:02x}'.format((mac >> elements) & 0xff) 
                        for elements in range(0, 2 * 6, 2)][::-1])
    except Exception:
        return ""


def _get_fallback_machine_code() -> str:
    """
    获取备用机器码（基于UUID和平台信息）
    
    Returns:
        str: 备用机器码
    """
    try:
        # 获取MAC地址
        mac = uuid.getnode()
        
        # 获取平台信息
        platform_info = f"{platform.node()}{platform.machine()}{platform.processor()}"
        
        # 组合并生成哈希值作为机器码
        device_string = f"{mac}{platform_info}"
        return hashlib.md5(device_string.encode()).hexdigest()
    except Exception:
        # 最后的备用方案：生成随机UUID
        return str(uuid.uuid4())