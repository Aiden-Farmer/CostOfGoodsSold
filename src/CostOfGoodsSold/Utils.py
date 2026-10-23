from collections.abc import Mapping
from contextlib import suppress
from datetime import datetime
from decimal import Decimal, InvalidOperation
from operator import itemgetter
from types import NoneType, UnionType
from typing import (
    Any,
    NamedTuple,
    get_args,
    get_origin,
    get_type_hints,
)
from typing_extensions import TypeForm

from .Errors import DataValidationError
from .Models import SupportedSalesChannels


###############################################################################
#
#                           Constants

_EMPTY_STR_IS_NONE = True 
_CONVERSION_ERRORS = ValueError, KeyError, InvalidOperation

###############################################################################

def convert[T](element: Any, _type: TypeForm[T]) -> T:
    """Converts element to datatype, caller responsible for handling ValueErrors""" 
 
    converters = {
        str: _cnv_str,
        datetime: _cnv_datetime,
        SupportedSalesChannels: _cnv_SupportedSalesChannel
    }
    def convert_union() -> TypeForm[T]: 
        multi_type = get_args(_type)
        # check for None first to capture '' str.
        if NoneType in multi_type:
            if _check_for_none(element): 
                return None # noqa

            # remove NoneType from multi_type
            multi_type = [t for t in multi_type if t is not NoneType]
        for t in multi_type:
            with suppress(*(_CONVERSION_ERRORS)):
                if t in converters:
                    return converters[t](element)
                return t(element) 
        raise ValueError(f"{element!r} not a valid instance of any [{multi_type.__repr__}]")

    if get_origin(_type) is UnionType:
        return convert_union()

    if _type in converters: 
        return converters[_type](element)

    return _type(element)

################################################################################
#                                                                              #
#                           Converters                                         #
#                                                                              #
################################################################################

def _cnv_datetime(element) -> datetime:

    def _is_mm_dd_yyyy_date_str(o: str):
        parts = o.split("/")
        
        # Check that there are three parts: mm, dd, yyyy
        if not len(parts) == 3:
            return False

        # Check that final part is 4 char long: yyyy 
        if not len(parts[2]) == 4:
            return False

        # Meets conditions
        return True

    if type(element) == str and _is_mm_dd_yyyy_date_str(element): return datetime.strptime(element, "%m/%d/%Y")
    if type(element) == int: return datetime.fromordinal(element) 
    if type(element) == str: return datetime.fromisoformat(element) 
    if type(element) == tuple and len(element) == 3: return datetime.fromisocalendar(*(element)) 
    raise ValueError("%s not a valid date format",element) 

def _cnv_str(o) -> str:
    if o == "":
        raise ValueError("Empty string is not considered valid string")
    return str(o)

def _check_for_none(o) -> bool:
    if o is None or _EMPTY_STR_IS_NONE and o == "":
        return True

    return False

def _cnv_SupportedSalesChannel(o) -> SupportedSalesChannels:
    if o is None:
        raise DataValidationError("SupportedSalesChannels must not be None")
    return SupportedSalesChannels[o]



###############################################################################
#
#                       Reader methods
#
###############################################################################

def validate_mapping[T: NamedTuple](return_type: type[T], mapping: Mapping[str, int | str]) -> bool:
    """Validates that all elements of NamedTuple return type are present in mapping and data, and that data types match."""
    for f in return_type._fields:
        if f not in mapping:
            return False
    return True

def build_row[T: NamedTuple](row, types, return_type: type[T]): 
    return return_type._make([convert(item, _type) for item, _type in zip(row, types)]
)

###############################################################################
#
#                       Reader 
#
###############################################################################

class RowReader[T: NamedTuple]:
    """
    Reader that accepts List|Tuple|Dict with map of indices|keys.

    Usage:
        reader = RowReader(NamedTuple subclass, mapping)
        data = reader(List|Tuple|Dict)
    Data will be a validated instance of NamedTuple subclass.
    
    params:
        return_type: NamedTuple subclass, i.e. InventoryRecord | PurchaseRecord | SalesRecord.
        mapping: dict[str, int|str] where key is NamedTuple field and value is index|key to access 
            item in data container that RowReader will be passed.

    """
    def __init__(self, return_type: type[T], 
        mapping: Mapping[str, int|str]):

        validate_mapping(return_type, mapping)
        self.return_type = return_type
        #field types relies on ordering of get_tpe_hints dict matching named_tuple, would likely be better to explicitly match
        self._field_types = get_type_hints(return_type).values()
        self._get = itemgetter( *(mapping[f] for f in return_type._fields))

    def __call__(self, row) -> T: 
        try:
            return build_row(self._get(row), self._field_types, self.return_type)
        except(_CONVERSION_ERRORS) as e:
            raise DataValidationError(f"row {row!r} could not be converted to {self.return_type}") from e
