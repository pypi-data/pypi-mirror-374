"""Telephone number history schema"""

from typing import Literal

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""

type phone_number_type = Literal[
    "personal", "functional", "external", "blocked", "legacy"
]


class TelephoneNumber(BaseSchemaModel):

    telephone_number: str
    telephone_type: phone_number_type
    partition: str | None
    assignment: str | None
    use: str | None
    comment: str | None

    table = "phone_numbers_v2"


class TelephoneNumberDiff(BaseDiffSchemaModel):

    telephone_type: FieldDiff[phone_number_type] = None
    partition: FieldDiff[str | None] = None
    assignment: FieldDiff[str | None] = None
    use: FieldDiff[str | None] = None
    comment: FieldDiff[str | None] = None

    table = "phone_numbers_v2"


class TelephoneNumberDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "phone_numbers_v2"
