"""
会话管理模型
"""
from dataclasses import dataclass
from typing import Optional
from ..utils.device_info import get_device_info
from .cdkey_login_response import CDKeyLoginResponse


@dataclass
class CDKeySession:
    """
    卡密会话管理模型，用于存储登录状态和token信息
    """
    # 登录响应对象
    login_response: Optional[CDKeyLoginResponse] = None
    
    # 卡密
    cdkey: Optional[str] = None
    
    # 项目密钥
    project_secret: Optional[str] = None
    
    # 项目UUID
    project_uuid: Optional[str] = None
    
    # 设备信息
    device_info: Optional[str] = None
    
    # API基础URL
    base_url: str = "http://api.privateapi.xyz:9000"
    
    def __post_init__(self):
        """
        初始化时自动获取设备信息（如果未提供）
        """
        if self.device_info is None:
            self.device_info = get_device_info()
    
    @property
    def token(self) -> Optional[str]:
        """
        获取当前会话的token
        
        Returns:
            Optional[str]: token值，如果未登录则返回None
        """
        if self.login_response and self.login_response.success:
            return self.login_response.token
        return None
        
    @property
    def is_logged_in(self) -> bool:
        """
        检查是否已登录且token有效
        
        Returns:
            bool: 已登录且token有效返回True，否则返回False
        """
        return self.token is not None
        
    def update_login_response(self, response: CDKeyLoginResponse):
        """
        更新登录响应
        
        Args:
            response (CDKeyLoginResponse): 登录响应对象
        """
        self.login_response = response
        
    def clear(self):
        """
        清除会话信息
        """
        self.login_response = None