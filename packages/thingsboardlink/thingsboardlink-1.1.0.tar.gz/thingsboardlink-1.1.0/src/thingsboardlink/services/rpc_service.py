"""
thingsboardlink RPC 服务模块

本模块提供 RPC（远程过程调用）相关的 API 调用功能。
包括单向和双向 RPC 调用，支持设备控制和通信。
"""

import time
from typing import Optional, Dict, Any

from ..models import RPCRequest, RPCResponse, PersistentRPCRequest
from ..exceptions import ValidationError, RPCError, TimeoutError


class RpcService:
    """
    RPC 服务类

    提供 RPC 调用相关的所有操作。
    支持单向和双向 RPC 调用，以及超时处理。
    """

    def __init__(self, client):
        """
        初始化 RPC 服务

        Args:
            client: ThingsBoardClient 实例
        """
        self.client = client

    def send_one_way_rpc(self,
                         device_id: str,
                         method: str,
                         params: Optional[Dict[str, Any]] = None) -> bool:
        """
        发送单向 RPC 请求

        单向 RPC 不等待设备响应，适用于设备控制命令。

        Args:
            device_id: 设备 ID
            method: RPC 方法名
            params: RPC 参数

        Returns:
            bool: 发送是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串",
                actual_value=method,
                message="RPC 方法名不能为空"
            )

        rpc_request = RPCRequest(
            method=method.strip(),
            params=params or {},
            persistent=False
        )

        try:
            endpoint = f"/api/plugins/rpc/oneway/{device_id}"
            response = self.client.post(
                endpoint,
                data=rpc_request.to_dict()
            )

            return response.status_code == 200

        except Exception as e:
            raise RPCError(
                message=f"发送单向 RPC 请求失败: {str(e)}",
                method_name=method,
                device_id=device_id
            )

    def send_two_way_rpc(self,
                         device_id: str,
                         method: str,
                         params: Optional[Dict[str, Any]] = None,
                         timeout_seconds: float = 30.0) -> RPCResponse:
        """
        发送双向 RPC 请求

        双向 RPC 等待设备响应，适用于需要获取设备状态或数据的场景。

        Args:
            device_id: 设备 ID
            method: RPC 方法名
            params: RPC 参数
            timeout_seconds: 超时时间（秒）

        Returns:
            RPCResponse: RPC 响应对象

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
            TimeoutError: RPC 调用超时时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串",
                actual_value=method,
                message="RPC 方法名不能为空"
            )

        if timeout_seconds <= 0:
            raise ValidationError(
                field_name="timeout_seconds",
                expected_type="正数",
                actual_value=timeout_seconds,
                message="超时时间必须大于 0"
            )

        rpc_request = RPCRequest(
            method=method.strip(),
            params=params or {},
            timeout=int(timeout_seconds * 1000),  # 转换为毫秒
            persistent=False
        )

        try:
            endpoint = f"/api/plugins/rpc/twoway/{device_id}"

            # 使用自定义超时时间
            response = self.client.post(
                endpoint,
                data=rpc_request.to_dict(),
                timeout=timeout_seconds + 5  # 给网络请求额外的缓冲时间
            )

            if response.status_code == 200:
                response_data = response.json()

                # 创建 RPC 响应对象
                rpc_response = RPCResponse(
                    id=response_data.get("id", ""),
                    method=method,
                    response=response_data,
                    timestamp=int(time.time() * 1000)
                )

                return rpc_response
            else:
                raise RPCError(
                    message=f"双向 RPC 调用失败，状态码: {response.status_code}",
                    method_name=method,
                    device_id=device_id
                )

        except TimeoutError:
            raise TimeoutError(
                message=f"双向 RPC 调用超时",
                timeout_seconds=timeout_seconds,
                operation=f"RPC {method}"
            )
        except Exception as e:
            if isinstance(e, (ValidationError, RPCError, TimeoutError)):
                raise
            raise RPCError(
                message=f"发送双向 RPC 请求失败: {str(e)}",
                method_name=method,
                device_id=device_id,
                timeout_seconds=timeout_seconds
            )

    def send_rpc_with_retry(self,
                            device_id: str,
                            method: str,
                            params: Optional[Dict[str, Any]] = None,
                            max_retries: int = 3,
                            timeout_seconds: float = 30.0,
                            retry_delay: float = 1.0) -> RPCResponse:
        """
        发送带重试的双向 RPC 请求

        Args:
            device_id: 设备 ID
            method: RPC 方法名
            params: RPC 参数
            max_retries: 最大重试次数
            timeout_seconds: 每次请求的超时时间（秒）
            retry_delay: 重试延迟（秒）

        Returns:
            RPCResponse: RPC 响应对象

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: 所有重试都失败时抛出
        """
        if max_retries < 0:
            raise ValidationError(
                field_name="max_retries",
                expected_type="非负整数",
                actual_value=max_retries,
                message="最大重试次数不能小于 0"
            )

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return self.send_two_way_rpc(
                    device_id=device_id,
                    method=method,
                    params=params,
                    timeout_seconds=timeout_seconds
                )

            except (RPCError, TimeoutError) as e:
                last_error = e

                if attempt < max_retries:
                    # 等待后重试
                    time.sleep(retry_delay)
                    continue
                else:
                    # 所有重试都失败
                    break

        # 抛出最后一个错误
        if last_error:
            raise last_error
        else:
            raise RPCError(
                message=f"发送 RPC 请求失败，已重试 {max_retries} 次",
                method_name=method,
                device_id=device_id
            )

    def send_persistent_rpc(self,
                            device_id: str,
                            method: str,
                            params: Optional[Dict[str, Any]] = None,
                            expiration_time: Optional[int] = None) -> str:
        """
        发送持久化 RPC 请求

        持久化 RPC 请求会被存储在服务器端，即使设备离线也能接收到请求。
        当设备重新连接时，会收到待处理的持久化 RPC 请求。

        Args:
            device_id: 设备 ID
            method: RPC 方法名
            params: RPC 参数
            expiration_time: 过期时间（毫秒时间戳），可选

        Returns:
            str: 持久化 RPC 请求的 ID

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
        """
        if not device_id or not device_id.strip():
            raise ValidationError(
                field_name="device_id",
                expected_type="非空字符串",
                actual_value=device_id,
                message="设备 ID 不能为空"
            )

        if not method or not method.strip():
            raise ValidationError(
                field_name="method",
                expected_type="非空字符串",
                actual_value=method,
                message="RPC 方法名不能为空"
            )

        rpc_request = {
            "method": method.strip(),
            "params": params or {},
            "persistent": True
        }

        if expiration_time is not None:
            rpc_request["expirationTime"] = expiration_time

        try:
            endpoint = f"/api/rpc/twoway/{device_id}"
            response = self.client.post(
                endpoint,
                data=rpc_request
            )

            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("rpcId", "")
            else:
                raise RPCError(
                    message=f"发送持久化 RPC 请求失败，状态码: {response.status_code}",
                    method_name=method,
                    device_id=device_id
                )

        except Exception as e:
            if isinstance(e, (ValidationError, RPCError)):
                raise
            raise RPCError(
                message=f"发送持久化 RPC 请求失败: {str(e)}",
                method_name=method,
                device_id=device_id
            )

    def get_persistent_rpc_response(self,
                                    rpc_id: str) -> Optional[PersistentRPCRequest]:
        """
        获取持久化 RPC 响应

        查询指定持久化 RPC 请求的当前状态和响应数据。

        Args:
            rpc_id: 持久化 RPC 请求的 ID

        Returns:
            Optional[PersistentRPCRequest]: 持久化 RPC 请求对象，如果不存在则返回 None

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空"
            )

        try:
            endpoint = f"/api/rpc/persistent/{rpc_id.strip()}"
            response = self.client.get(endpoint)

            if response.status_code == 200:
                response_data = response.json()
                return PersistentRPCRequest.from_dict(response_data)
            elif response.status_code == 404:
                return None
            else:
                raise RPCError(
                    message=f"获取持久化 RPC 响应失败，状态码: {response.status_code}",
                    method_name="get_persistent_rpc_response"
                )

        except Exception as e:
            if isinstance(e, (ValidationError, RPCError)):
                raise
            raise RPCError(
                message=f"获取持久化 RPC 响应失败: {str(e)}"
            )

    def delete_persistent_rpc(self, rpc_id: str) -> bool:
        """
        删除持久化 RPC 请求

        删除指定的持久化 RPC 请求。已完成的请求可以被删除以清理存储。

        Args:
            rpc_id: 持久化 RPC 请求的 ID

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空"
            )

        try:
            endpoint = f"/api/rpc/persistent/{rpc_id.strip()}"
            response = self.client.delete(endpoint)

            return response.status_code == 200

        except Exception as e:
            raise RPCError(
                message=f"删除持久化 RPC 请求失败: {str(e)}"
            )

    def wait_for_persistent_rpc_response(self,
                                         rpc_id: str,
                                         timeout_seconds: float = 60.0,
                                         poll_interval: float = 2.0) -> Optional[PersistentRPCRequest]:
        """
        等待持久化 RPC 响应

        轮询持久化 RPC 请求直到收到响应或超时。

        Args:
            rpc_id: 持久化 RPC 请求的 ID
            timeout_seconds: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）

        Returns:
            Optional[PersistentRPCRequest]: 完成的持久化 RPC 请求对象，超时则返回 None

        Raises:
            ValidationError: 参数验证失败时抛出
            RPCError: RPC 调用失败时抛出
            TimeoutError: 等待超时时抛出
        """
        if not rpc_id or not rpc_id.strip():
            raise ValidationError(
                field_name="rpc_id",
                expected_type="非空字符串",
                actual_value=rpc_id,
                message="RPC 请求 ID 不能为空"
            )

        if timeout_seconds <= 0:
            raise ValidationError(
                field_name="timeout_seconds",
                expected_type="正数",
                actual_value=timeout_seconds,
                message="超时时间必须大于 0"
            )

        if poll_interval <= 0:
            raise ValidationError(
                field_name="poll_interval",
                expected_type="正数",
                actual_value=poll_interval,
                message="轮询间隔必须大于 0"
            )

        start_time = time.time()
        rpc_id = rpc_id.strip()

        try:
            while time.time() - start_time < timeout_seconds:
                # 获取当前请求状态
                rpc_request = self.get_persistent_rpc_response(rpc_id)

                if rpc_request is None:
                    raise RPCError(
                        message=f"持久化 RPC 请求 {rpc_id} 不存在"
                    )

                # 检查是否已完成
                if rpc_request.is_completed:
                    return rpc_request

                # 检查是否已过期
                if rpc_request.is_expired:
                    return rpc_request

                # 等待下次轮询
                time.sleep(poll_interval)

            # 超时
            raise TimeoutError(
                message=f"等待持久化 RPC 响应超时",
                timeout_seconds=timeout_seconds,
                operation=f"等待 RPC {rpc_id}"
            )

        except Exception as e:
            if isinstance(e, (ValidationError, RPCError, TimeoutError)):
                raise
            raise RPCError(
                message=f"等待持久化 RPC 响应失败: {str(e)}"
            )
