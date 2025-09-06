"""
thingsboardlink 设备服务模块

本模块提供设备管理相关的 API 调用功能。
包括设备的创建、查询、更新、删除以及凭证管理等操作。
"""
from typing import List, Optional, Dict, Any

from ..models import Device, DeviceCredentials, PageData
from ..exceptions import NotFoundError, DeviceError, ValidationError


class DeviceService:
    """
    设备服务类

    提供设备管理相关的所有操作。
    包括 CRUD 操作、凭证管理和批量查询等功能。
    """

    def __init__(self, client):
        """
        初始化设备服务

        Args:
            client: ThingsBoardClient 实例
        """
        self.client = client

    def create_device(self,
                      name: str,
                      device_type: str = "default",
                      label: Optional[str] = None,
                      additional_info: Optional[Dict[str, Any]] = None) -> Device:
        """
        创建设备

        Args:
            name: 设备名称
            device_type: 设备类型
            label: 设备标签
            additional_info: 附加信息

        Returns:
            Device: 创建的设备对象

        Raises:
            ValidationError: 参数验证失败时抛出
            DeviceError: 设备创建失败时抛出
        """
        if not name or not name.strip():
            raise ValidationError(
                field_name="name",
                expected_type="非空字符串",
                actual_value=name,
                message="设备名称不能为空"
            )

        device = Device(
            name=name.strip(),
            type=device_type,
            label=label,
            additional_info=additional_info or {}
        )

        try:
            response = self.client.post(
                "/api/device",
                data=device.to_dict()
            )

            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            raise DeviceError(
                message=f"创建设备失败: {str(e)}",
                device_name=name
            )

    def get_device_by_id(self, device_id: str) -> Device:
        """
        根据 ID 获取设备

        Args:
            device_id: 设备 ID

        Returns:
            Device: 设备对象

        Raises:
            NotFoundError: 设备不存在时抛出
            ValidationError: 参数验证失败时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        try:
            response = self.client.get(f"/api/device/{device_id}")
            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备",
                    resource_id=device_id
                )
            raise DeviceError(
                f"获取设备失败: {str(e)}",
                device_id=device_id
            )

    def update_device(self, device: Device) -> Device:
        """
        更新设备信息

        Args:
            device: 设备对象

        Returns:
            Device: 更新后的设备对象

        Raises:
            ValidationError: 参数验证失败时抛出
            DeviceError: 设备更新失败时抛出
        """
        if not device.id:
            raise ValidationError(
                field_name="device.id",
                expected_type="非空字符串",
                actual_value=device.id,
                message="设备 ID 不能为空"
            )

        if not device.name or not device.name.strip():
            raise ValidationError(
                field_name="device.name",
                expected_type="非空字符串",
                actual_value=device.name,
                message="设备名称不能为空"
            )

        try:
            response = self.client.post(
                "/api/device",
                data=device.to_dict()
            )

            device_data = response.json()
            return Device.from_dict(device_data)

        except Exception as e:
            raise DeviceError(
                message=f"更新设备失败: {str(e)}",
                device_id=device.id,
                device_name=device.name
            )

    def delete_device(self, device_id: str) -> bool:
        """
        删除设备

        Args:
            device_id: 设备 ID

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            DeviceError: 设备删除失败时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        try:
            response = self.client.delete(f"/api/device/{device_id}")
            return response.status_code == 200

        except Exception as e:
            raise DeviceError(
                f"删除设备失败: {str(e)}",
                device_id=device_id
            )

    def get_tenant_devices(self,
                           page_size: int = 10,
                           page: int = 0,
                           text_search: Optional[str] = None,
                           sort_property: Optional[str] = None,
                           sort_order: Optional[str] = None) -> PageData:
        """
        获取租户下的设备列表

        Args:
            page_size: 页面大小
            page: 页码（从 0 开始）
            text_search: 文本搜索
            sort_property: 排序属性
            sort_order: 排序顺序（ASC/DESC）

        Returns:
            PageData: 分页设备数据

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if page_size <= 0:
            raise ValidationError(
                field_name="page_size",
                expected_type="正整数 | Positive integer",
                actual_value=page_size,
                message="页面大小必须大于 0 | Page size must be greater than 0"
            )

        if page < 0:
            raise ValidationError(
                field_name="page",
                expected_type="非负整数 | Non-negative integer",
                actual_value=page,
                message="页码不能小于 0 | Page number cannot be less than 0"
            )

        params = {
            "pageSize": page_size,
            "page": page
        }

        if text_search:
            params["textSearch"] = text_search
        if sort_property:
            params["sortProperty"] = sort_property
        if sort_order:
            params["sortOrder"] = sort_order

        try:
            response = self.client.get(
                "/api/tenant/devices",
                params=params
            )

            page_data = response.json()
            return PageData.from_dict(page_data, Device)

        except Exception as e:
            raise DeviceError(
                f"获取设备列表失败 | Failed to get device list: {str(e)}"
            )

    def get_device_credentials(self, device_id: str) -> DeviceCredentials:
        """
        获取设备凭证

        Args:
            device_id: 设备 ID

        Returns:
            DeviceCredentials: 设备凭证对象

        Raises:
            ValidationError: 参数验证失败时抛出
            NotFoundError: 设备不存在时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        try:
            response = self.client.get(f"/api/device/{device_id}/credentials")
            credentials_data = response.json()
            return DeviceCredentials.from_dict(credentials_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="设备凭证",
                    resource_id=device_id
                )
            raise DeviceError(
                message=f"获取设备凭证失败: {str(e)}",
                device_id=device_id
            )

    def get_devices_by_name(self, device_name: str) -> List[Device]:
        """
        根据名称搜索设备

        Args:
            device_name: 设备名称

        Returns:
            List[Device]: 匹配的设备列表

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not device_name or not device_name.strip():
            raise ValidationError(
                field_name="device_name",
                expected_type="非空字符串",
                actual_value=device_name,
                message="设备名称不能为空"
            )

        try:
            # 使用分页查询搜索设备
            page_data = self.get_tenant_devices(
                page_size=100,  # 获取更多结果
                text_search=device_name.strip()
            )

            # 过滤精确匹配的设备
            matching_devices = [
                device for device in page_data.data
                if device.name.lower() == device_name.lower()
            ]

            return matching_devices

        except Exception as e:
            raise DeviceError(
                f"搜索设备失败: {str(e)}",
                device_name=device_name
            )

    def device_exists(self, device_id: str) -> bool:
        """
        检查设备是否存在

        Args:
            device_id: 设备 ID

        Returns:
            bool: 设备是否存在
        """
        try:
            self.get_device_by_id(device_id)
            return True
        except NotFoundError:
            return False
        except Exception:
            return False
