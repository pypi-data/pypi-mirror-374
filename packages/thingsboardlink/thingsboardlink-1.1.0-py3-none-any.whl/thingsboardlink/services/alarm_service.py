"""
thingsboardlink 警报服务模块

本模块提供警报管理相关的 API 调用功能。
包括警报的创建、查询、确认、清除等操作。
"""

from typing import List, Optional, Dict, Any

from ..models import Alarm, AlarmSeverity, AlarmStatus, PageData
from ..exceptions import ValidationError, AlarmError, NotFoundError


class AlarmService:
    """
    警报服务类

    提供警报管理相关的所有操作。
    包括警报的创建、查询、状态管理等功能。
    """

    def __init__(self, client):
        """
        初始化警报服务

        Args:
            client: ThingsBoardClient 实例
        """
        self.client = client

    def create_alarm(self,
                     alarm_type: str,
                     originator_id: str,
                     severity: AlarmSeverity = AlarmSeverity.CRITICAL,
                     details: Optional[Dict[str, Any]] = None,
                     propagate: bool = True) -> Alarm:
        """
        创建警报

        Args:
            alarm_type: 警报类型
            originator_id: 发起者 ID（通常是设备 ID）
            severity: 警报严重程度
            details: 警报详情
            propagate: 是否传播警报

        Returns:
            Alarm: 创建的警报对象

        Raises:
            ValidationError: 参数验证失败时抛出
            AlarmError: 警报创建失败时抛出
        """
        if not alarm_type or not alarm_type.strip():
            raise ValidationError(
                field_name="alarm_type",
                expected_type="非空字符串",
                actual_value=alarm_type,
                message="警报类型不能为空"
            )

        if not originator_id or not originator_id.strip():
            raise ValidationError(
                field_name="originator_id",
                expected_type="非空字符串",
                actual_value=originator_id,
                message="发起者 ID 不能为空"
            )

        alarm = Alarm(
            type=alarm_type.strip(),
            originator_id=originator_id.strip(),
            severity=severity,
            status=AlarmStatus.ACTIVE_UNACK,
            details=details or {},
            propagate=propagate
        )

        try:
            response = self.client.post(
                "/api/alarm",
                data=alarm.to_dict()
            )

            alarm_data = response.json()
            return Alarm.from_dict(alarm_data)

        except Exception as e:
            raise AlarmError(
                message=f"创建警报失败: {str(e)}",
                alarm_type=alarm_type
            )

    def get_alarm(self, alarm_id: str) -> Alarm:
        """
        根据 ID 获取警报

        Args:
            alarm_id: 警报 ID

        Returns:
            Alarm: 警报对象

        Raises:
            ValidationError: 参数验证失败时抛出
            NotFoundError: 警报不存在时抛出
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串",
                actual_value=alarm_id,
                message="警报 ID 不能为空"
            )

        try:
            response = self.client.get(f"/api/alarm/{alarm_id}")
            alarm_data = response.json()
            return Alarm.from_dict(alarm_data)

        except Exception as e:
            if "404" in str(e) or "Not Found" in str(e):
                raise NotFoundError(
                    resource_type="警报",
                    resource_id=alarm_id
                )
            raise AlarmError(
                message=f"获取警报失败: {str(e)}",
                alarm_id=alarm_id
            )

    def get_alarms(self,
                   originator_id: str,
                   page_size: int = 10,
                   page: int = 0,
                   text_search: Optional[str] = None,
                   sort_property: Optional[str] = None,
                   sort_order: Optional[str] = None,
                   start_time: Optional[int] = None,
                   end_time: Optional[int] = None,
                   fetch_originator: bool = False,
                   status_list: Optional[List[AlarmStatus]] = None,
                   severity_list: Optional[List[AlarmSeverity]] = None,
                   type_list: Optional[List[str]] = None) -> PageData:
        """
        获取警报列表

        Args:
            originator_id: 发起者 ID
            page_size: 页面大小
            page: 页码（从 0 开始）
            text_search: 文本搜索
            sort_property: 排序属性
            sort_order: 排序顺序（ASC/DESC）
            start_time: 开始时间戳（毫秒）
            end_time: 结束时间戳（毫秒）
            fetch_originator: 是否获取发起者信息
            status_list: 状态过滤列表
            severity_list: 严重程度过滤列表
            type_list: 类型过滤列表

        Returns:
            PageData: 分页警报数据

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not originator_id or not originator_id.strip():
            raise ValidationError(
                field_name="originator_id",
                expected_type="非空字符串",
                actual_value=originator_id,
                message="发起者 ID 不能为空"
            )

        if page_size <= 0:
            raise ValidationError(
                field_name="page_size",
                expected_type="正整数",
                actual_value=page_size,
                message="页面大小必须大于 0"
            )

        if page < 0:
            raise ValidationError(
                field_name="page",
                expected_type="非负整数",
                actual_value=page,
                message="页码不能小于 0"
            )

        try:
            params = {
                "pageSize": page_size,
                "page": page,
                "fetchOriginator": str(fetch_originator).lower()
            }

            if text_search:
                params["textSearch"] = text_search
            if sort_property:
                params["sortProperty"] = sort_property
            if sort_order:
                params["sortOrder"] = sort_order
            if start_time is not None:
                params["startTime"] = start_time
            if end_time is not None:
                params["endTime"] = end_time

            # 状态过滤
            if status_list:
                params["statusList"] = ",".join([status.value for status in status_list])

            # 严重程度过滤
            if severity_list:
                params["severityList"] = ",".join([severity.value for severity in severity_list])

            # 类型过滤
            if type_list:
                params["typeList"] = ",".join(type_list)

            endpoint = f"/api/alarm/DEVICE/{originator_id}"
            response = self.client.get(endpoint, params=params)

            page_data = response.json()
            return PageData.from_dict(page_data, Alarm)

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise AlarmError(
                f"获取警报列表失败: {str(e)}"
            )

    def ack_alarm(self, alarm_id: str) -> bool:
        """
        确认警报

        Args:
            alarm_id: 警报 ID

        Returns:
            bool: 确认是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            AlarmError: 警报确认失败时抛出
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串",
                actual_value=alarm_id,
                message="警报 ID 不能为空"
            )

        try:
            response = self.client.post(f"/api/alarm/{alarm_id}/ack")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                message=f"确认警报失败: {str(e)}",
                alarm_id=alarm_id
            )

    def clear_alarm(self, alarm_id: str) -> bool:
        """
        清除警报

        Args:
            alarm_id: 警报 ID

        Returns:
            bool: 清除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            AlarmError: 警报清除失败时抛出
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串",
                actual_value=alarm_id,
                message="警报 ID 不能为空"
            )

        try:
            response = self.client.post(f"/api/alarm/{alarm_id}/clear")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                message=f"清除警报失败: {str(e)}",
                alarm_id=alarm_id
            )

    def delete_alarm(self, alarm_id: str) -> bool:
        """
        删除警报

        Args:
            alarm_id: 警报 ID

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            AlarmError: 警报删除失败时抛出
        """
        if not alarm_id or not alarm_id.strip():
            raise ValidationError(
                field_name="alarm_id",
                expected_type="非空字符串",
                actual_value=alarm_id,
                message="警报 ID 不能为空"
            )

        try:
            response = self.client.delete(f"/api/alarm/{alarm_id}")
            return response.status_code == 200

        except Exception as e:
            raise AlarmError(
                message=f"删除警报失败: {str(e)}",
                alarm_id=alarm_id
            )

    def alarm_exists(self, alarm_id: str) -> bool:
        """
        检查警报是否存在

        Args:
            alarm_id: 警报 ID

        Returns:
            bool: 警报是否存在
        """
        try:
            self.get_alarm(alarm_id)
            return True
        except NotFoundError:
            return False
        except Exception:
            return False
