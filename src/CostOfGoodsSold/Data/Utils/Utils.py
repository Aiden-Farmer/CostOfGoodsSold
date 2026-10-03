from typing import (NamedTuple, TypeVar, Generic, Any, get_type_hints,
get_origin, get_args)
from types import NoneType, UnionType 
from operator import itemgetter
from contextlib import suppress
from datetime import datetime
from decimal import Decimal, InvalidOperation

T = TypeVar("T", bound=NamedTuple)

_EMPTY_STR_IS_NONE = True 

_CONVERSION_ERRORS = ValueError, KeyError, InvalidOperation

class DataValidationError(Exception):
    ...

def convert(element: Any, _type:Any): 
    """Converts element to datatype, caller responsible for handling ValueErrors""" 
 
    converters = {
        int: _cnv_int,
        str: _cnv_str,
        datetime: _cnv_datetime,
        Decimal: _cnv_decimal,
    }
    def convert_union(): 
        multi_type = get_args(_type)
        print(multi_type)        
        # check for None first to capture '' str.
        if NoneType in multi_type:
            if _check_for_none(element): 
                return None

            # remove NoneType from multi_type
            multi_type = [t for t in multi_type if t is not NoneType]
            print(multi_type)
        for t in multi_type:
            with suppress(*(_CONVERSION_ERRORS)):
                return converters[t](element)
        
        raise ValueError(f"{element!r} not a valid instance of any [{multi_type.__repr__}]")

    if get_origin(_type) is UnionType:
        return convert_union()

    return converters[_type](element)


################################################################################
#                                                                              #
#                           Converters                                         #
#                                                                              #
################################################################################

def _cnv_datetime(element) -> datetime:
    if type(element) == int: return datetime.fromordinal(element) 
    if type(element) == str: return datetime.fromisoformat(element) 
    if type(element) == tuple and len(element) == 3: return datetime.fromisocalendar(*(element)) 
    raise ValueError("%s not a valid date format",element) 

def _cnv_int(o) -> int:
    return int(o)

def _cnv_str(o) -> str:
    if o == "":
        raise ValueError("Empty string is not considered valid string")
    return str(o)

def _cnv_decimal(o) -> Decimal:
    return Decimal(o)

def _check_for_none(o) -> bool:
    if o is None:
        return True

    elif _EMPTY_STR_IS_NONE and o == "":
        return True

    return False

###############################################################################
#
#                       Reader methods
#
###############################################################################

def validate_mapping(return_type: type[T], mapping: dict[str, int|str]) -> bool:
    """Validates that all elements of NamedTuple return type are present in
    mapping and data, and that data types match."""
    for f in return_type._fields:
        if f not in mapping:
            return False
    return True

def build_row(row, types, return_type: type[T]): 
        return return_type._make(*(convert(item, _type) for item, _type in zip(row, types)))

###############################################################################
#
#                       Reader 
#
###############################################################################

class RowReader(Generic[T]):
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
        mapping: dict[str, int|str]):

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
