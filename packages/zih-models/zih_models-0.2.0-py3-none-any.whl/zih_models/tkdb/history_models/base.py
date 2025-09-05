"""base helper things for all schemas"""

from enum import StrEnum
from typing import ClassVar, Literal

from pydantic import BaseModel


class ChangeAction(StrEnum):

    CREATED = "created"
    DELETED = "deleted"
    MODIFIED = "modified"


class FieldDiffObject[T](BaseModel):
    old: T
    new: T


type FieldDiff[T] = FieldDiffObject[T] | None

TABLE = Literal[
    "functional_numbers",
    "phone_numbers_v2",
    "personal_numbers",
    "users_v2",
    "external_numbers",
]


class BaseSchemaModel(BaseModel):
    """Base model with table classvar"""

    table: ClassVar[TABLE]
    action: ClassVar[ChangeAction] = ChangeAction.CREATED

    def get_user_logins(self) -> set[str]:
        return set()

    def get_ous(self) -> set[str]:
        return set()


class BaseDiffSchemaModel(BaseSchemaModel):
    """base for all diff models"""

    action: ClassVar[ChangeAction] = ChangeAction.MODIFIED

    def has_changes(self) -> bool:
        for field in type(self).model_fields:
            if getattr(self, field) is not None:
                return True
        return False


class BaseDeleteSchemaModel(BaseSchemaModel):
    """base for all delete models"""

    action: ClassVar[ChangeAction] = ChangeAction.DELETED
