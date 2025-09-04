from enum import IntEnum
from typing import Any

from asyncpg import Range, Point  # Box, Polygon,
from tortoise import Model
from tortoise.contrib.postgres.fields import ArrayField
from tortoise.fields import Field, SmallIntField, IntField, FloatField, DatetimeField, BinaryField, BigIntField
from tortoise.fields.base import VALUE


class UniqBinaryField(BinaryField):
    indexable = True


class UInt1Field(SmallIntField):
    SQL_TYPE = "SMALLINT"  # UINT2

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": 255,
        }


class UInt2Field(IntField):
    SQL_TYPE = "INT"  # UINT2

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": 65535,
        }


class UIntField(BigIntField):
    SQL_TYPE = "BIGINT"  # UINT4

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": 4_294_967_295,
        }


class UInt8Field(BigIntField):
    SQL_TYPE = "BIGINT"  # UINT8

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": 18_446_744_073_709_551_615,
        }


class UInt16Field(BigIntField):
    SQL_TYPE = "BIGINT"  # UINT16

    @property
    def constraints(self) -> dict:
        return {
            "ge": 0,
            "le": 340282366920938463463374607431768211455,
        }


class ListField(Field[VALUE]):
    base_field = Field[VALUE]
    labels: tuple

    def to_python_value(self, value):
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(*value)
        self.validate(value)
        return value


class CollectionField(ListField[VALUE]):
    labels: tuple
    step: str = None

    def __new__(cls, precision: int = 0, *args, **kwargs):
        if precision:
            cls.step = f"0.{'0'*(precision-1)}1"
        cls.base_field = FloatField if precision else IntField
        return super().__new__(cls)


class RangeField(CollectionField[Range]):
    field_type = Range
    labels = ("from", "to")

    def __new__(cls, precision: int = 0, *args, **kwargs):
        cls.SQL_TYPE = "numrange" if precision else "int4range"
        return super().__new__(cls)

    def to_python_value(self, value: tuple):
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(*[float(v) for v in value])
        self.validate(value)
        return (value.lower, value.upper) if value else None

    def to_db_value(self, value: Any, instance: Model) -> Any:
        if value is not None and not isinstance(value, self.field_type):
            value = self.field_type(*value)  # pylint: disable=E1102
        self.validate(value)
        return value


class PointField(CollectionField[Point]):
    SQL_TYPE = "POINT"
    field_type = Point
    base_field = FloatField
    labels = ("lat", "lon")


#
#
# class PolygonField(ListField[Polygon]):
#     SQL_TYPE = "POLYGON"
#     field_type = Polygon
#     base_field = PointField
#
#
# class BoxField(ListField[Box]):
#     SQL_TYPE = "BOX"
#     field_type = Box
#     base_field = PointField


class DatetimeSecField(DatetimeField):
    class _db_postgres:
        SQL_TYPE = "TIMESTAMPTZ(0)"


class SetField(ListField[IntEnum]):
    SQL_TYPE = "smallint[]"
    field_type = ArrayField
    base_field = SmallIntField
    enum_type: type[IntEnum]

    def __init__(self, enum_type: type[IntEnum], **kwargs: Any):
        super().__init__(**kwargs)
        self.enum_type = enum_type
        self.field_type = enum_type
        self.base_field = enum_type

    def to_python_value(self, value):
        for val in value:
            if val is not None and not isinstance(val, self.enum_type):
                val = self.enum_type(val)
            self.validate(val)
        return value
