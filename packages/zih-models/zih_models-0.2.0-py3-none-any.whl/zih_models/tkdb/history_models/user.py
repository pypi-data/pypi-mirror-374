"""User history schema"""

from typing import override

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""


class User(BaseSchemaModel):

    uid: str
    personal_numbers: list[str]
    functional_numbers: list[str]

    table = "users_v2"

    @override
    def get_user_logins(self) -> set[str]:
        logins = super().get_user_logins()
        logins.add(self.uid)
        return logins


class UserDiff(BaseDiffSchemaModel):

    personal_numbers: FieldDiff[list[str]] = None
    functional_numbers: FieldDiff[list[str]] = None

    table = "users_v2"


class UserDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "users_v2"
