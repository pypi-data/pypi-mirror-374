"""
卡密登录响应模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CDKeyLoginResponse:
    """
    卡密登录响应参数模型
    """
    # 剩余秒数
    remaining_time: int
    
    # 登录结果签名,用于防止返回的数据被篡改
    sign: str
    
    # 时间戳13或者10位数都行,时间戳就是1970年
    timestamp: str
    
    # Token用于心跳
    token: str
    
    # 使用窗口
    use_window: int
    
    # 窗口数量
    window_number: int
    
    # 1 登录成功,其他值看msg
    code: int
    
    # 消息
    msg: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CDKeyLoginResponse':
        """
        从字典数据创建CDKeyLoginResponse对象
        
        Args:
            data (dict): 响应数据字典
            
        Returns:
            CDKeyLoginResponse: 响应对象实例
        """
        return cls(
            remaining_time=int(data.get("RemainingTime", 0)),
            sign=data.get("Sign", ""),
            timestamp=data.get("Timestamp", ""),
            token=data.get("Token", ""),
            use_window=int(data.get("UseWindow", 0)),
            window_number=int(data.get("WindowNumber", 0)),
            code=int(data.get("code", 0)),
            msg=data.get("msg", "")
        )
        
    def is_success(self) -> bool:
        """
        判断登录是否成功
        
        Returns:
            bool: 登录成功返回True，否则返回False
        """
        return self.code == 1
        
    @property
    def success(self) -> bool:
        """
        登录是否成功的属性
        
        Returns:
            bool: 登录成功返回True，否则返回False
        """
        return self.is_success()