"""
thingsboardlink - 专为 Python 开发者设计的高级 IoT 平台交互工具包
"""

# 版本消息
__version__ = "1.1.0"
__author__ = "Miraitowa-la"
__email__ = "2056978412@qq.com"
__description__ = "一个专为 Python 开发者设计的高级 IoT 平台交互工具包"

# 导入核心类
from .client import ThingsBoardClient
from .exceptions import (
    ThingsBoardError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    APIError,
    ConnectionError,
    TimeoutError,
    ConfigurationError,
    RateLimitError,
    DeviceError,
    TelemetryError,
    AlarmError,
    RPCError
)
from .models import (
    Device,
    DeviceCredentials,
    TelemetryData,
    Attribute,
    RpcPersistentStatus,
    Alarm,
    RPCRequest,
    RPCResponse,
    EntityRelation,
    EntityId,
    PageData,
    TimeseriesData,
    EntityType,
    AlarmSeverity,
    AlarmStatus,
    AttributeScope
)

from .services import (
    DeviceService,
    TelemetryService,
    AttributeService,
    AlarmService,
    RpcService,
    RelationService
)

# 公开API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__description__",

    # 核心客户端
    "ThingsBoardClient",

    # 异常类
    "ThingsBoardError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "APIError",
    "ConnectionError",
    "TimeoutError",
    "ConfigurationError",
    "RateLimitError",
    "DeviceError",
    "TelemetryError",
    "AlarmError",
    "RPCError",

    # 数据模型
    "Device",
    "DeviceCredentials",
    "TelemetryData",
    "Attribute",
    "RpcPersistentStatus",
    "Alarm",
    "RPCRequest",
    "RPCResponse",
    "EntityRelation",
    "EntityId",
    "PageData",
    "TimeseriesData",
    "EntityType",
    "AlarmSeverity",
    "AlarmStatus",
    "AttributeScope",

    # 服务类 | Service classes
    "DeviceService",
    "TelemetryService",
    "AttributeService",
    "AlarmService",
    "RpcService",
    "RelationService"
]
