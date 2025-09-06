"""
thingsboardlink 数据模型模块

本模块定义了与 ThingsBoard 平台交互时使用的所有数据模型。
这些模型提供了类型安全的数据结构和便捷的数据转换方法。
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class EntityType(Enum):
    """
    实体类型枚举

    Attributes:
        DEVICE: 设备
        ASSET: 资产
        USER: 用户
        CUSTOMER: 客户
        TENANT: 租户
        RULE_CHAIN: 规则链
        RULE_NODE: 规则节点
        DASHBOARD: 仪表盘
        WIDGET_TYPE: 部件类型
        WIDGET_BUNDLE: 部件包
        ALARM: 告警
    """
    DEVICE = "DEVICE"
    ASSET = "ASSET"
    USER = "USER"
    CUSTOMER = "CUSTOMER"
    TENANT = "TENANT"
    RULE_CHAIN = "RULE_CHAIN"
    RULE_NODE = "RULE_NODE"
    DASHBOARD = "DASHBOARD"
    WIDGET_TYPE = "WIDGET_TYPE"
    WIDGET_BUNDLE = "WIDGET_BUNDLE"
    ALARM = "ALARM"


class AlarmSeverity(Enum):
    """
    警报严重程度枚举

    Attributes:
        CRITICAL: 关键级别
        MAJOR: 主要级别
        MINOR: 次要级别
        WARNING: 警告级别
        INDETERMINATE: 不确定级别
    """
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    WARNING = "WARNING"
    INDETERMINATE = "INDETERMINATE"


class AlarmStatus(Enum):
    """
    警报状态枚举

    Attributes:
        ACTIVE_UNACK: 活动且未确认
        ACTIVE_ACK: 活动且已确认
        CLEARED_UNACK: 已清除但未确认
        CLEARED_ACK: 已清除且已确认
    """
    ACTIVE_UNACK = "ACTIVE_UNACK"
    ACTIVE_ACK = "ACTIVE_ACK"
    CLEARED_UNACK = "CLEARED_UNACK"
    CLEARED_ACK = "CLEARED_ACK"


class AttributeScope(Enum):
    """
    属性范围枚举

    Attributes:
        CLIENT_SCOPE: 客户端属性，由设备设置并推送到服务器。
        SERVER_SCOPE: 服务端属性，由服务器设置并可推送到设备。
        SHARED_SCOPE: 共享属性，由服务器设置，对所有客户端可见。
    """
    CLIENT_SCOPE = "CLIENT_SCOPE"
    SERVER_SCOPE = "SERVER_SCOPE"
    SHARED_SCOPE = "SHARED_SCOPE"


class RpcPersistentStatus(Enum):
    """
    RPC 持久化状态枚举

    Attributes:
        QUEUED: 已排队 - RPC 已创建并保存到数据库，尚未发送到设备
        SENT: 已发送 - ThingsBoard 已尝试将 RPC 发送到设备
        DELIVERED: 已送达 - 设备已确认 RPC（单向 RPC 的最终状态）
        SUCCESSFUL: 成功 - ThingsBoard 已收到双向 RPC 的回复
        TIMEOUT: 超时 - 传输层检测到 RPC 超时
        EXPIRED: 过期 - RPC 在配置的到期时间内未送达或未收到回复
        FAILED: 失败 - 在配置的重试次数内未能传递 RPC，或设备不支持此类命令
    """
    QUEUED = "QUEUED"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    SUCCESSFUL = "SUCCESSFUL"
    TIMEOUT = "TIMEOUT"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


@dataclass
class EntityId:
    """实体 ID 模型"""
    id: str
    entity_type: EntityType

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "entityType": self.entity_type.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityId':
        """从字典创建实体 ID"""
        return cls(
            id=data["id"],
            entity_type=EntityType(data["entityType"])
        )


@dataclass
class Device:
    """
    设备模型
    
    表示 ThingsBoard 中的设备实体。
    包含设备的基本信息和元数据。
    """
    name: str
    type: str = "default"
    id: Optional[str] = None
    label: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None
    created_time: Optional[datetime] = None
    customer_id: Optional[EntityId] = None
    tenant_id: Optional[EntityId] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.additional_info is None:
            self.additional_info = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "name": self.name,
            "type": self.type,
            "label": self.label,
            "additionalInfo": self.additional_info or {}
        }

        if self.id:
            result["id"] = {"id": self.id, "entityType": "DEVICE"}
        if self.customer_id:
            result["customerId"] = self.customer_id.to_dict()
        if self.tenant_id:
            result["tenantId"] = self.tenant_id.to_dict()
        if self.created_time:
            result["createdTime"] = int(self.created_time.timestamp() * 1000)

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Device':
        """从字典创建设备对象"""
        device_id = None
        if "id" in data and isinstance(data["id"], dict):
            device_id = data["id"].get("id")
        elif "id" in data and isinstance(data["id"], str):
            device_id = data["id"]

        customer_id = None
        if "customerId" in data and data["customerId"]:
            customer_id = EntityId.from_dict(data["customerId"])

        tenant_id = None
        if "tenantId" in data and data["tenantId"]:
            tenant_id = EntityId.from_dict(data["tenantId"])

        created_time = None
        if "createdTime" in data and data["createdTime"]:
            created_time = datetime.fromtimestamp(data["createdTime"] / 1000)

        return cls(
            id=device_id,
            name=data.get("name", ""),
            type=data.get("type", "default"),
            label=data.get("label"),
            additional_info=data.get("additionalInfo", {}),
            created_time=created_time,
            customer_id=customer_id,
            tenant_id=tenant_id
        )


@dataclass
class DeviceCredentials:
    """设备凭证模型"""
    device_id: str
    credentials_type: str = "ACCESS_TOKEN"
    credentials_id: Optional[str] = None
    credentials_value: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "deviceId": {"id": self.device_id, "entityType": "DEVICE"},
            "credentialsType": self.credentials_type,
            "credentialsId": self.credentials_id,
            "credentialsValue": self.credentials_value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceCredentials':
        """从字典创建设备凭证对象"""
        device_id = data["deviceId"]
        if isinstance(device_id, dict):
            device_id = device_id["id"]

        credentials_type = data.get("credentialsType", "ACCESS_TOKEN")
        credentials_id = data.get("credentialsId")
        credentials_value = data.get("credentialsValue")

        # 对于 ACCESS_TOKEN 类型，如果 credentialsValue 为空但 credentialsId 有值，
        # 则使用 credentialsId 作为实际的访问令牌
        if credentials_type == "ACCESS_TOKEN" and not credentials_value and credentials_id:
            credentials_value = credentials_id

        return cls(
            device_id=device_id,
            credentials_type=credentials_type,
            credentials_id=credentials_id,
            credentials_value=credentials_value
        )


@dataclass
class TelemetryData:
    """
    遥测数据模型
    
    表示设备的遥测数据点。
    包含键值对数据和时间戳信息。
    """
    key: str
    value: Union[str, int, float, bool]
    timestamp: Optional[int] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.timestamp is None:
            self.timestamp = int(time.time() * 1000)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "ts": self.timestamp,
            "values": {self.key: self.value}
        }

    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> 'TelemetryData':
        """从字典创建遥测数据对象"""
        return cls(
            key=key,
            value=data.get("value"),
            timestamp=data.get("ts")
        )

    @staticmethod
    def create_batch(data: Dict[str, Union[str, int, float, bool]],
                     timestamp: Optional[int] = None) -> List['TelemetryData']:
        """
        创建批量遥测数据
        
        Args:
            data: 键值对数据字典
            timestamp: 时间戳（可选）
            
        Returns:
            List[TelemetryData]: 遥测数据列表
        """
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        return [TelemetryData(key=k, value=v, timestamp=timestamp)
                for k, v in data.items()]


@dataclass
class Attribute:
    """
    属性模型
    
    表示实体的属性信息。
    支持客户端、服务端和共享属性。
    """
    key: str
    value: Any
    scope: AttributeScope = AttributeScope.SERVER_SCOPE
    last_update_ts: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            self.key: self.value
        }

    @classmethod
    def from_api_response(cls, key: str, data: Dict[str, Any],
                          scope: AttributeScope = AttributeScope.SERVER_SCOPE) -> 'Attribute':
        """从 API 响应创建属性对象"""
        return cls(
            key=key,
            value=data.get('value'),
            scope=scope,
            last_update_ts=data.get('lastUpdateTs')
        )

    @staticmethod
    def create_batch(data: Dict[str, Any],
                     scope: AttributeScope = AttributeScope.SERVER_SCOPE) -> List['Attribute']:
        """
        创建批量属性
        
        Args:
            data: 属性数据字典
            scope: 属性范围
            
        Returns:
            List[Attribute]: 属性列表
        """
        return [Attribute(key=k, value=v, scope=scope) for k, v in data.items()]


@dataclass
class Alarm:
    """
    警报模型
    
    表示系统中的警报信息。
    包含警报类型、严重程度、状态等信息。
    """
    type: str
    originator_id: str
    severity: AlarmSeverity = AlarmSeverity.CRITICAL
    status: AlarmStatus = AlarmStatus.ACTIVE_UNACK
    id: Optional[str] = None
    start_ts: Optional[int] = None
    end_ts: Optional[int] = None
    ack_ts: Optional[int] = None
    clear_ts: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    propagate: bool = True

    def __post_init__(self):
        """初始化后处理"""
        if self.details is None:
            self.details = {}
        if self.start_ts is None:
            self.start_ts = int(time.time() * 1000)

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        result = {
            "originator": {"id": self.originator_id, "entityType": "DEVICE"},
            "type": self.type,
            "severity": self.severity.value,
            "status": self.status.value,
            "startTs": self.start_ts,
            "details": self.details,
            "propagate": self.propagate
        }

        if self.id:
            result["id"] = {"id": self.id, "entityType": "ALARM"}
        if self.end_ts:
            result["endTs"] = self.end_ts
        if self.ack_ts:
            result["ackTs"] = self.ack_ts
        if self.clear_ts:
            result["clearTs"] = self.clear_ts

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alarm':
        """从字典创建警报对象"""
        alarm_id = None
        if "id" in data and isinstance(data["id"], dict):
            alarm_id = data["id"].get("id")
        elif "id" in data and isinstance(data["id"], str):
            alarm_id = data["id"]

        originator_id = data["originator"]
        if isinstance(originator_id, dict):
            originator_id = originator_id["id"]

        return cls(
            id=alarm_id,
            type=data.get("type", ""),
            originator_id=originator_id,
            severity=AlarmSeverity(data.get("severity", "CRITICAL")),
            status=AlarmStatus(data.get("status", "ACTIVE_UNACK")),
            start_ts=data.get("startTs"),
            end_ts=data.get("endTs"),
            ack_ts=data.get("ackTs"),
            clear_ts=data.get("clearTs"),
            details=data.get("details", {}),
            propagate=data.get("propagate", True)
        )


@dataclass
class RPCRequest:
    """RPC 请求模型"""
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    persistent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "method": self.method,
            "params": self.params
        }

        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.persistent:
            result["persistent"] = self.persistent

        return result


@dataclass
class RPCResponse:
    """RPC 响应模型"""
    id: str
    method: str
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[int] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.timestamp is None:
            self.timestamp = int(time.time() * 1000)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RPCResponse':
        """从字典创建 RPC 响应对象"""
        return cls(
            id=data.get("id", ""),
            method=data.get("method", ""),
            response=data.get("response"),
            error=data.get("error"),
            timestamp=data.get("timestamp")
        )

    @property
    def is_success(self) -> bool:
        """检查 RPC 调用是否成功"""
        return self.error is None


@dataclass
class PersistentRPCRequest:
    """持久化 RPC 请求模型"""
    id: Optional[str] = None
    device_id: Optional[str] = None
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    expiration_time: Optional[int] = None
    status: str = RpcPersistentStatus.QUEUED.value
    created_time: Optional[int] = None
    response: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.created_time is None:
            self.created_time = int(time.time() * 1000)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "method": self.method,
            "params": self.params
        }

        if self.id is not None:
            result["rpcId"] = self.id  # ThingsBoard 使用 rpcId
        if self.device_id is not None:
            result["deviceId"] = self.device_id
        if self.expiration_time is not None:
            result["expirationTime"] = self.expiration_time
        if self.status:
            result["status"] = self.status
        if self.created_time is not None:
            result["createdTime"] = self.created_time
        if self.response is not None:
            result["response"] = self.response

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersistentRPCRequest':
        """从字典创建持久化RPC请求对象"""
        return cls(
            id=data.get("rpcId") or data.get("id"),  # ThingsBoard 可能使用 rpcId 或 id
            device_id=data.get("deviceId"),
            method=data.get("method", ""),
            params=data.get("params", {}),
            expiration_time=data.get("expirationTime"),
            status=data.get("status", RpcPersistentStatus.QUEUED.value),
            created_time=data.get("createdTime") or data.get("creationTime"),
            response=data.get("response")
        )

    @property
    def is_completed(self) -> bool:
        """检查RPC请求是否已完成"""
        return self.status in [RpcPersistentStatus.SUCCESSFUL.value,
                               RpcPersistentStatus.FAILED.value,
                               RpcPersistentStatus.EXPIRED.value]

    @property
    def is_expired(self) -> bool:
        """检查RPC请求是否已过期"""
        if self.expiration_time is None:
            return False
        return int(time.time() * 1000) > self.expiration_time


@dataclass
class EntityRelation:
    """实体关系模型"""
    from_id: EntityId
    to_id: EntityId
    type: str
    type_group: str = "COMMON"
    additional_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """初始化后处理 """
        if self.additional_info is None:
            self.additional_info = {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "from": self.from_id.to_dict(),
            "to": self.to_id.to_dict(),
            "type": self.type,
            "typeGroup": self.type_group,
            "additionalInfo": self.additional_info
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EntityRelation':
        """从字典创建实体关系对象"""
        return cls(
            from_id=EntityId.from_dict(data["from"]),
            to_id=EntityId.from_dict(data["to"]),
            type=data.get("type", ""),
            type_group=data.get("typeGroup", "COMMON"),
            additional_info=data.get("additionalInfo", {})
        )


@dataclass
class PageData:
    """分页数据模型"""
    data: List[Any]
    total_pages: int
    total_elements: int
    has_next: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_class=None) -> 'PageData':
        """从字典创建分页数据对象"""
        items = data.get("data", [])
        if item_class and hasattr(item_class, 'from_dict'):
            items = [item_class.from_dict(item) for item in items]

        return cls(
            data=items,
            total_pages=data.get("totalPages", 0),
            total_elements=data.get("totalElements", 0),
            has_next=data.get("hasNext", False)
        )


@dataclass
class TimeseriesData:
    """时间序列数据模型"""
    key: str
    values: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, key: str, data: List[Dict[str, Any]]) -> 'TimeseriesData':
        """从字典创建时间序列数据对象"""
        return cls(key=key, values=data)

    def get_latest_value(self) -> Optional[Any]:
        """获取最新值"""
        if not self.values:
            return None
        return max(self.values, key=lambda x: x.get('ts', 0)).get('value')

    def get_values_in_range(self, start_ts: int, end_ts: int) -> List[Dict[str, Any]]:
        """获取指定时间范围内的值"""
        return [v for v in self.values
                if start_ts <= v.get('ts', 0) <= end_ts]

    def __len__(self) -> int:
        """支持len()函数，返回values的长度"""
        return len(self.values)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """支持下标操作，直接访问values中的元素"""
        return self.values[index]
