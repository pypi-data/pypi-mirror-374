"""
thingsboardlink 异常处理模块

该模块定义了 thingsboardlink 软件包中使用的所有自定义异常类。
这些异常类提供了详细的错误信息和分层的异常处理机制。
"""
from typing import Dict, Any, Optional


class ThingsBoardError(Exception):
    """
    ThingsBoard 基础异常类

    所有 thingsboardlink 相关异常基类。
    提供统一的异常处理接口和基础功能。
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化异常

        Args:
            message: 错误信息
            details: 错误详情字典
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class AuthenticationError(ThingsBoardError):
    """
    认证错误

    当用户认证失败时抛出此异常。
    包括登录失败、令牌过期、权限不足等情况。
    """

    def __init__(self, message: str = "认证失败",
                 details: Optional[Dict[str, Any]] = None):
        """
        初始化认证错误异常

        Args:
            message: 错误信息
            details: 错误详情字典
        """
        super().__init__(message, details)


class NotFoundError(ThingsBoardError):
    """
    资源未找到错误

    当请求的资源不存在时抛出此异常。
    包括设备、用户、警报等资源未找到的情况。
    """

    def __init__(self, resource_type: str = "资源",
                 resource_id: Optional[str] = None,
                 message: Optional[str] = None):
        """
        初始化资源未找到错误异常

        Args:
            resource_type: 资源类型
            resource_id: 资源ID
            message: 错误信息
        """
        if message is None:
            if resource_id:
                message = f"{resource_type} '{resource_id}' 未找到"
            else:
                message = f"{resource_type} 未找到"

        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message, details)


class ValidationError(ThingsBoardError):
    """
    数据验证错误

    当输入数据不符合预期格式或约束时抛出此异常。
    包括参数类型错误、值范围错误、必填字段缺失等情况。
    """

    def __init__(self, field_name: Optional[str] = None,
                 expected_type: Optional[str] = None,
                 actual_value: Any = None,
                 message: Optional[str] = None):
        """
        初始化数据验证错误异常

        Args:
            field_name: 字段名称
            expected_type: 期望类型
            actual_value: 实际值
            message: 错误信息
        """
        if message is None:
            if field_name and expected_type:
                message = f"字段 '{field_name}' 验证失败，期望类型：{expected_type}"
            else:
                message = "数据验证失败"

        details = {
            "field_name": field_name,
            "expected_type": expected_type,
            "actual_value": actual_value
        }
        super().__init__(message, details)


class APIError(ThingsBoardError):
    """
    API 调用错误

    当 API 调用返回错误状态码时抛出此异常。
    包含详细的 HTTP 状态码和响应数据。
    """

    def __init__(self, message: str,
                 status_code: Optional[int] = None,
                 response_data: Optional[Dict[str, Any]] = None,
                 request_url: Optional[str] = None,
                 request_method: Optional[str] = None):
        """
        初始化 API 调用错误异常

        Args:
            message: 错误信息
            status_code: 状态码
            response_data: 响应数据
            request_url: 请求地址
            request_method: 请求方法
        """
        details = {
            "status_code": status_code,
            "response_data": response_data,
            "request_url": request_url,
            "request_method": request_method
        }
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_url = request_url
        self.request_method = request_method

    @classmethod
    def from_response(cls, response, message: Optional[str] = None):
        """
        从 HTTP 响应创建 API 调用错误异常

        Args:
            response: HTTP 响应对象
            message: 错误消息
        Return:
            API 调用错误异常
        """
        if message is None:
            message = f"API 调用失败，状态码: {response.status_code}"

        try:
            response_data = response.json()
        except (ValueError, AttributeError):
            response_data = {"raw_response": response.text if hasattr(response, 'text') else str(response)}

        return cls(
            message=message,
            status_code=getattr(response, 'status_code', None),
            response_data=response_data,
            request_url=getattr(response, 'url', None),
            request_method=getattr(response.request, 'method', None) if hasattr(response, 'request') else None
        )


class ConnectionError(ThingsBoardError):
    """
    连接错误

    当无法连接到 ThingsBoard 服务器时抛出此异常。
    包括网络连接失败、服务器不可达等情况。
    """

    def __init__(self, message: str = "无法连接到 ThingsBoard 服务器",
                 server_url: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """
        初始化连接错误异常

        Args:
            message: 错误消息
            server_url: 服务器地址
            details: 详情
        """
        if details is None:
            details = {}
        if server_url:
            details["server_url"] = server_url
        super().__init__(message, details)


class TimeoutError(ThingsBoardError):
    """
    超时错误

    当请求超时时抛出此异常。
    包括连接超时、读取超时等情况。
    """

    def __init__(self, message: str = "请求超时",
                 timeout_seconds: Optional[float] = None,
                 operation: Optional[str] = None):
        """
        初始化超时错误异常

        Args:
            message: 错误消息
            timeout_seconds: 超时时间
            operation: 操作
        """
        details = {
            "timeout_seconds": timeout_seconds,
            "operation": operation
        }
        super().__init__(message, details)


class ConfigurationError(ThingsBoardError):
    """
    配置错误

    当配置参数无效或缺失时抛出此异常。
    包括服务器地址错误、认证信息缺失等情况。
    """

    def __init__(self, message: str = "配置错误",
                 config_key: Optional[str] = None,
                 expected_value: Optional[str] = None):
        """
        初始化配置错误异常

        Args:
            message: 错误消息
            config_key: 配置键
            expected_value: 期望值
        """
        details = {
            "config_key": config_key,
            "expected_value": expected_value
        }
        super().__init__(message, details)


class RateLimitError(APIError):
    """
    速率限制错误

    当 API 调用超过速率限制时抛出此异常。
    包含重试建议和限制信息。
    """

    def __init__(self, message: str = "API 调用速率超限",
                 retry_after: Optional[int] = None,
                 limit_type: Optional[str] = None):
        """
        初始化速率限制错误异常

        Args:
            message: 错误消息
            retry_after: 重试
            limit_type: 限制类型
        """
        details = {
            "retry_after": retry_after,
            "limit_type": limit_type
        }
        super().__init__(message, status_code=429, response_data=details)


class DeviceError(ThingsBoardError):
    """
    设备相关错误

    设备操作相关的错误。
    包括设备创建失败、设备状态异常等情况。
    """

    def __init__(self, message: str,
                 device_id: Optional[str] = None,
                 device_name: Optional[str] = None):
        """
        初始化设备相关错误异常

        Args:
            message: 错误消息
            device_id: 设备标识符号
            device_name: 设备名称
        """
        details = {
            "device_id": device_id,
            "device_name": device_name
        }
        super().__init__(message, details)


class TelemetryError(ThingsBoardError):
    """
    遥测数据相关错误

    遥测数据操作相关的错误。
    包括数据格式错误、上传失败等情况。
    """

    def __init__(self, message: str,
                 data_key: Optional[str] = None,
                 data_value: Any = None):
        """
        初始化遥测数据相关错误异常

        Args:
            message: 错误消息
            data_key: 数据键
            data_value: 数据值
        """
        details = {
            "data_key": data_key,
            "data_value": data_value
        }
        super().__init__(message, details)


class AlarmError(ThingsBoardError):
    """
    警报相关错误

    警报操作相关的错误。
    包括警报创建失败、状态更新失败等情况。
    """

    def __init__(self, message: str,
                 alarm_id: Optional[str] = None,
                 alarm_type: Optional[str] = None):
        """
        初始化遥测数据相关错误异常

        Args:
            message: 错误消息
            alarm_id: 报警ID
            alarm_type: 报警类型
        """
        details = {
            "alarm_id": alarm_id,
            "alarm_type": alarm_type
        }
        super().__init__(message, details)


class RPCError(ThingsBoardError):
    """
    RPC 调用相关错误

    RPC 调用相关的错误。
    包括调用超时、设备无响应等情况。
    """

    def __init__(self, message: str,
                 method_name: Optional[str] = None,
                 device_id: Optional[str] = None,
                 timeout_seconds: Optional[float] = None):
        """
        初始化 RPC 调用相关错误异常

        Args:
            message: 错误消息
            method_name: 方法名称
            device_id: 设备标识符
            timeout_seconds: 超时时间
        """
        details = {
            "method_name": method_name,
            "device_id": device_id,
            "timeout_seconds": timeout_seconds
        }
        super().__init__(message, details)
