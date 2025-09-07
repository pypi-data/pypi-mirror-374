"""
卡密API客户端模块
"""
import requests
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..models.cdkey_login_request import CDKeyLoginRequest
from ..models.cdkey_login_response import CDKeyLoginResponse
from ..models.cdkey_heartbeat_request import CDKeyHeartbeatRequest
from ..models.cdkey_heartbeat_response import CDKeyHeartbeatResponse
from ..models.config import CDKeyConfig
from ..models.session import CDKeySession
from ..utils.helpers import generate_sign, generate_heartbeat_sign, get_timestamp


class CDKeyClient:
    """
    卡密登录API客户端
    """
    
    def __init__(self, config: Optional[CDKeyConfig] = None, base_url: str = "http://api.privateapi.xyz:9000"):
        """
        初始化客户端
        
        Args:
            config (Optional[CDKeyConfig]): 配置对象，如果提供则使用其中的参数
            base_url (str): API基础URL，仅在未提供config时使用
        """
        if config:
            self.config = config
            self.base_url = config.base_url
            # 初始化会话
            self.session = CDKeySession(
                cdkey=config.cdkey,
                project_secret=config.project_secret,
                project_uuid=config.project_uuid,
                device_info=config.device_info,
                base_url=config.base_url
            )
        else:
            self.config = None
            self.base_url = base_url
            self.session = CDKeySession(base_url=base_url)
        
        # 创建带重试机制的会话
        self._http_session = self._create_http_session()
    
    def _create_http_session(self) -> requests.Session:
        """
        创建带重试机制的HTTP会话
        
        Returns:
            requests.Session: 配置了重试机制的会话对象
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 总重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
        )
        
        # 创建适配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        
        # 为HTTP和HTTPS请求设置适配器
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认超时时间
        session.timeout = 30
        
        return session
    
    def login(self, 
              cdkey: Optional[str] = None, 
              project_secret: Optional[str] = None, 
              project_uuid: Optional[str] = None, 
              device_info: Optional[str] = None,
              timestamp: Optional[str] = None) -> CDKeyLoginResponse:
        """
        执行卡密登录
        
        Args:
            cdkey (Optional[str]): 卡密，如果未提供则使用配置中的参数
            project_secret (Optional[str]): 项目密钥，如果未提供则使用配置中的参数
            project_uuid (Optional[str]): 项目UUID，如果未提供则使用配置中的参数
            device_info (Optional[str]): 设备信息，如果未提供则使用配置中的参数
            timestamp (Optional[str]): 时间戳，如果未提供将自动生成
            
        Returns:
            CDKeyLoginResponse: 登录响应对象
        """
        try:
            # 如果提供了配置对象或会话，则使用其中的参数
            if self.config:
                cdkey = cdkey or self.config.cdkey
                project_secret = project_secret or self.config.project_secret
                project_uuid = project_uuid or self.config.project_uuid
                device_info = device_info or self.config.device_info
            elif self.session:
                cdkey = cdkey or self.session.cdkey
                project_secret = project_secret or self.session.project_secret
                project_uuid = project_uuid or self.session.project_uuid
                device_info = device_info or self.session.device_info
            
            # 检查必要参数
            if not all([cdkey, project_secret, project_uuid, device_info]):
                return CDKeyLoginResponse(
                    remaining_time=0,
                    sign="",
                    timestamp="",
                    token="",
                    use_window=0,
                    window_number=0,
                    code=-1,
                    msg="缺少必要参数"
                )
                
            # 如果没有提供时间戳，则自动生成13位时间戳
            if timestamp is None:
                timestamp = get_timestamp(13)
                
            # 生成签名
            sign = generate_sign(cdkey, project_secret, project_uuid, device_info, timestamp)
            
            # 构造请求对象
            request_data = CDKeyLoginRequest(
                sign=sign,
                timestamp=timestamp,
                cdkey=cdkey,
                cdkey_device_info=device_info,
                project_uuid=project_uuid
            )
            
            # 发送POST请求
            url = f"{self.base_url}/cdkey/v2/script/verify/login"
            response = self._http_session.post(url, data=request_data.to_dict(), timeout=30)
            
            # 解析响应
            if response.status_code == 200:
                response_data = response.json()
                login_response = CDKeyLoginResponse.from_dict(response_data)
                # 更新会话中的登录响应
                self.session.update_login_response(login_response)
                return login_response
            else:
                # 返回错误响应
                error_response = CDKeyLoginResponse(
                    remaining_time=0,
                    sign="",
                    timestamp="",
                    token="",
                    use_window=0,
                    window_number=0,
                    code=response.status_code,
                    msg=f"请求失败: {response.status_code}"
                )
                # 更新会话中的登录响应
                self.session.update_login_response(error_response)
                return error_response
        except requests.exceptions.ConnectionError as e:
            # 网络连接错误处理
            error_response = CDKeyLoginResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                token="",
                use_window=0,
                window_number=0,
                code=-1,
                msg=f"网络连接错误: {str(e)}"
            )
            # 更新会话中的登录响应
            self.session.update_login_response(error_response)
            return error_response
        except requests.exceptions.Timeout as e:
            # 超时错误处理
            error_response = CDKeyLoginResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                token="",
                use_window=0,
                window_number=0,
                code=-1,
                msg=f"请求超时: {str(e)}"
            )
            # 更新会话中的登录响应
            self.session.update_login_response(error_response)
            return error_response
        except Exception as e:
            # 其他异常处理
            error_response = CDKeyLoginResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                token="",
                use_window=0,
                window_number=0,
                code=-1,
                msg=f"请求异常: {str(e)}"
            )
            # 更新会话中的登录响应
            self.session.update_login_response(error_response)
            return error_response
            
    def heartbeat(self,
                  token: Optional[str] = None,
                  cdkey: Optional[str] = None,
                  project_secret: Optional[str] = None,
                  project_uuid: Optional[str] = None,
                  device_info: Optional[str] = None,
                  timestamp: Optional[str] = None) -> CDKeyHeartbeatResponse:
        """
        执行卡密心跳
        
        Args:
            token (Optional[str]): 登录成功时返回的token，如果未提供则使用会话中的token
            cdkey (Optional[str]): 卡密，如果未提供则使用配置或会话中的参数
            project_secret (Optional[str]): 项目密钥，如果未提供则使用配置或会话中的参数
            project_uuid (Optional[str]): 项目UUID，如果未提供则使用配置或会话中的参数
            device_info (Optional[str]): 设备信息（应与登录时使用的设备信息一致），如果未提供则使用配置或会话中的参数
            timestamp (Optional[str]): 时间戳，如果未提供将自动生成
            
        Returns:
            CDKeyHeartbeatResponse: 心跳响应对象
        """
        try:
            # 如果提供了配置对象或会话，则使用其中的参数
            if self.config:
                cdkey = cdkey or self.config.cdkey
                project_secret = project_secret or self.config.project_secret
                project_uuid = project_uuid or self.config.project_uuid
                device_info = device_info or self.config.device_info
            elif self.session:
                cdkey = cdkey or self.session.cdkey
                project_secret = project_secret or self.session.project_secret
                project_uuid = project_uuid or self.session.project_uuid
                device_info = device_info or self.session.device_info
            
            # 如果未提供token，则尝试从会话中获取
            if token is None and self.session:
                token = self.session.token
                
            # 检查必要参数
            if not all([token, cdkey, project_secret, project_uuid, device_info]):
                return CDKeyHeartbeatResponse(
                    remaining_time=0,
                    sign="",
                    timestamp="",
                    code=-1,
                    msg="缺少必要参数: " + ", ".join([k for k, v in {
                        "token": token, 
                        "cdkey": cdkey, 
                        "project_secret": project_secret, 
                        "project_uuid": project_uuid, 
                        "device_info": device_info
                    }.items() if not v])
                )
                
            # 如果没有提供时间戳，则自动生成13位时间戳
            if timestamp is None:
                timestamp = get_timestamp(13)
                
            # 生成签名
            sign = generate_heartbeat_sign(cdkey, token, project_secret, project_uuid, device_info, timestamp)
            
            # 构造请求对象
            request_data = CDKeyHeartbeatRequest(
                sign=sign,
                timestamp=timestamp,
                cdkey=cdkey,
                cdkey_device_info=device_info,
                project_uuid=project_uuid,
                token=token
            )
            
            # 发送POST请求
            url = f"{self.base_url}/cdkey/v2/script/verify/heartbeat"
            response = self._http_session.post(url, data=request_data.to_dict(), timeout=30)
            
            # 解析响应
            if response.status_code == 200:
                response_data = response.json()
                return CDKeyHeartbeatResponse.from_dict(response_data)
            else:
                # 返回错误响应
                return CDKeyHeartbeatResponse(
                    remaining_time=0,
                    sign="",
                    timestamp="",
                    code=response.status_code,
                    msg=f"请求失败: {response.status_code}"
                )
        except requests.exceptions.ConnectionError as e:
            # 网络连接错误处理
            return CDKeyHeartbeatResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                code=-1,
                msg=f"网络连接错误: {str(e)}"
            )
        except requests.exceptions.Timeout as e:
            # 超时错误处理
            return CDKeyHeartbeatResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                code=-1,
                msg=f"请求超时: {str(e)}"
            )
        except Exception as e:
            # 其他异常处理
            return CDKeyHeartbeatResponse(
                remaining_time=0,
                sign="",
                timestamp="",
                code=-1,
                msg=f"请求异常: {str(e)}"
            )