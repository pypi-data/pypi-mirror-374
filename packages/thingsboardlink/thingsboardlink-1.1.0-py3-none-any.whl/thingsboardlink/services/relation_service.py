"""
thingsboardlink 关系服务模块

本模块提供实体关系管理相关的 API 调用功能。
包括实体间关系的创建、删除、查询等操作。
"""

from typing import List, Optional, Dict, Any

from ..models import EntityRelation, EntityId, EntityType
from ..exceptions import ValidationError, APIError


class RelationService:
    """
    关系服务类

    提供实体关系管理相关的所有操作。
    支持实体间关系的完整生命周期管理。
    """

    def __init__(self, client):
        """
        初始化关系服务

        Args:
            client: ThingsBoardClient 实例
        """
        self.client = client

    def create_relation(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON",
                        additional_info: Optional[Dict[str, Any]] = None) -> EntityRelation:
        """
        创建实体关系

        Args:
            from_id: 源实体 ID
            from_type: 源实体类型
            to_id: 目标实体 ID
            to_type: 目标实体类型
            relation_type: 关系类型
            type_group: 类型组
            additional_info: 附加信息

        Returns:
            EntityRelation: 创建的关系对象

        Raises:
            ValidationError: 参数验证失败时抛出
            APIError: 关系创建失败时抛出
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串",
                actual_value=from_id,
                message="源实体 ID 不能为空"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串",
                actual_value=to_id,
                message="目标实体 ID 不能为空"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串g",
                actual_value=relation_type,
                message="关系类型不能为空"
            )

        relation = EntityRelation(
            from_id=EntityId(id=from_id.strip(), entity_type=from_type),
            to_id=EntityId(id=to_id.strip(), entity_type=to_type),
            type=relation_type.strip(),
            type_group=type_group,
            additional_info=additional_info or {}
        )

        try:
            response = self.client.post(
                "/api/relation",
                data=relation.to_dict()
            )

            if response.status_code == 200:
                return relation
            else:
                raise APIError(
                    message=f"创建实体关系失败，状态码: {response.status_code}",
                    status_code=response.status_code
                )

        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            raise APIError(
                f"创建实体关系失败: {str(e)}"
            )

    def delete_relation(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON") -> bool:
        """
        删除实体关系

        Args:
            from_id: 源实体 ID
            from_type: 源实体类型
            to_id: 目标实体 ID
            to_type: 目标实体类型
            relation_type: 关系类型
            type_group: 类型组

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
            APIError: 关系删除失败时抛出
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串",
                actual_value=from_id,
                message="源实体 ID 不能为空"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串",
                actual_value=to_id,
                message="目标实体 ID 不能为空"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串",
                actual_value=relation_type,
                message="关系类型不能为空"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationType": relation_type.strip(),
                "relationTypeGroup": type_group
            }

            response = self.client.delete("/api/relation", params=params)
            return response.status_code == 200

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"删除实体关系失败: {str(e)}"
            )

    def get_relation(self,
                     from_id: str,
                     from_type: EntityType,
                     to_id: str,
                     to_type: EntityType,
                     relation_type: str,
                     type_group: str = "COMMON") -> Optional[EntityRelation]:
        """
        获取实体关系

        Args:
            from_id: 源实体 ID
            from_type: 源实体类型
            to_id: 目标实体 ID
            to_type: 目标实体类型
            relation_type: 关系类型
            type_group: 类型组

        Returns:
            Optional[EntityRelation]: 关系对象，不存在时返回 None

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串",
                actual_value=from_id,
                message="源实体 ID 不能为空"
            )

        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串",
                actual_value=to_id,
                message="目标实体 ID 不能为空"
            )

        if not relation_type or not relation_type.strip():
            raise ValidationError(
                field_name="relation_type",
                expected_type="非空字符串",
                actual_value=relation_type,
                message="关系类型不能为空"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationType": relation_type.strip(),
                "relationTypeGroup": type_group
            }

            response = self.client.get("/api/relation", params=params)

            if response.status_code == 200:
                relation_data = response.json()
                return EntityRelation.from_dict(relation_data)
            elif response.status_code == 404:
                return None
            else:
                raise APIError(
                    message=f"获取实体关系失败，状态码: {response.status_code}",
                    status_code=response.status_code
                )

        except Exception as e:
            if isinstance(e, (ValidationError, APIError)):
                raise
            raise APIError(
                f"获取实体关系失败: {str(e)}"
            )

    def find_by_from(self,
                     from_id: str,
                     from_type: EntityType,
                     relation_type_group: str = "COMMON") -> List[EntityRelation]:
        """
        查找从指定实体出发的所有关系

        Args:
            from_id: 源实体 ID
            from_type: 源实体类型
            relation_type_group: 关系类型组

        Returns:
            List[EntityRelation]: 关系列表

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not from_id or not from_id.strip():
            raise ValidationError(
                field_name="from_id",
                expected_type="非空字符串",
                actual_value=from_id,
                message="源实体 ID 不能为空"
            )

        try:
            params = {
                "fromId": from_id.strip(),
                "fromType": from_type.value,
                "relationTypeGroup": relation_type_group
            }

            response = self.client.get("/api/relations", params=params)
            relations_data = response.json()

            return [EntityRelation.from_dict(rel) for rel in relations_data]

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"查找实体关系失败: {str(e)}"
            )

    def find_by_to(self,
                   to_id: str,
                   to_type: EntityType,
                   relation_type_group: str = "COMMON") -> List[EntityRelation]:
        """
        查找指向指定实体的所有关系

        Args:
            to_id: 目标实体 ID
            to_type: 目标实体类型
            relation_type_group: 关系类型组

        Returns:
            List[EntityRelation]: 关系列表

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not to_id or not to_id.strip():
            raise ValidationError(
                field_name="to_id",
                expected_type="非空字符串",
                actual_value=to_id,
                message="目标实体 ID 不能为空"
            )

        try:
            params = {
                "toId": to_id.strip(),
                "toType": to_type.value,
                "relationTypeGroup": relation_type_group
            }

            response = self.client.get("/api/relations", params=params)
            relations_data = response.json()

            return [EntityRelation.from_dict(rel) for rel in relations_data]

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"查找实体关系失败: {str(e)}"
            )

    def relation_exists(self,
                        from_id: str,
                        from_type: EntityType,
                        to_id: str,
                        to_type: EntityType,
                        relation_type: str,
                        type_group: str = "COMMON") -> bool:
        """
        检查实体关系是否存在

        Args:
            from_id: 源实体 ID
            from_type: 源实体类型
            to_id: 目标实体 ID
            to_type: 目标实体类型
            relation_type: 关系类型
            type_group: 类型组

        Returns:
            bool: 关系是否存在
        """
        try:
            relation = self.get_relation(
                from_id=from_id,
                from_type=from_type,
                to_id=to_id,
                to_type=to_type,
                relation_type=relation_type,
                type_group=type_group
            )
            return relation is not None
        except Exception:
            return False

    def delete_relations(self,
                         entity_id: str,
                         entity_type: EntityType,
                         direction: str = "FROM") -> bool:
        """
        删除实体的所有关系

        Args:
            entity_id: 实体 ID
            entity_type: 实体类型
            direction: 删除方向（FROM/TO/BOTH）

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败时抛出
        """
        if not entity_id or not entity_id.strip():
            raise ValidationError(
                field_name="entity_id",
                expected_type="非空字符串",
                actual_value=entity_id,
                message="实体 ID 不能为空"
            )

        if direction not in ["FROM", "TO", "BOTH"]:
            raise ValidationError(
                field_name="direction",
                expected_type="FROM、TO 或 BOTH",
                actual_value=direction,
                message="删除方向必须是 FROM、TO 或 BOTH"
            )

        try:
            success = True

            if direction in ["FROM", "BOTH"]:
                # 删除从该实体出发的关系 | Delete relations from this entity
                relations = self.find_by_from(entity_id, entity_type)
                for relation in relations:
                    result = self.delete_relation(
                        from_id=relation.from_id.id,
                        from_type=relation.from_id.entity_type,
                        to_id=relation.to_id.id,
                        to_type=relation.to_id.entity_type,
                        relation_type=relation.type,
                        type_group=relation.type_group
                    )
                    success = success and result

            if direction in ["TO", "BOTH"]:
                # 删除指向该实体的关系 | Delete relations to this entity
                relations = self.find_by_to(entity_id, entity_type)
                for relation in relations:
                    result = self.delete_relation(
                        from_id=relation.from_id.id,
                        from_type=relation.from_id.entity_type,
                        to_id=relation.to_id.id,
                        to_type=relation.to_id.entity_type,
                        relation_type=relation.type,
                        type_group=relation.type_group
                    )
                    success = success and result

            return success

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise APIError(
                f"删除实体关系失败: {str(e)}"
            )
