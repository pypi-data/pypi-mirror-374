"""
配置模型
"""
from dataclasses import dataclass
from typing import Optional
from ..utils.device_info import get_device_info


@dataclass
class CDKeyConfig:
    """
    卡密配置参数模型，用于存储共享的配置参数
    """
    # 卡密
    cdkey: str
    
    # 项目密钥
    project_secret: str
    
    # 项目UUID
    project_uuid: str
    
    # 设备信息
    device_info: str = None
    
    # API基础URL
    base_url: str = "http://api.privateapi.xyz:9000"
    
    def __post_init__(self):
        """
        数据验证和自动获取设备信息
        """
        if not self.cdkey:
            raise ValueError("卡密不能为空")
        if not self.project_secret:
            raise ValueError("项目密钥不能为空")
        if not self.project_uuid:
            raise ValueError("项目UUID不能为空")
        # 如果未提供设备信息，则自动获取
        if self.device_info is None:
            self.device_info = get_device_info()