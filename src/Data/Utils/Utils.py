from ..Data.Models import SalesRecord, InventoryRecord,
from typing import Generic, TypeVar
from annotationlib import get_annotations
from exceptions import BaseException

T = TypeVar("T")

class DataValidationError(BaseException)
    ...

def validate_positional_data(data: Tuple|List, mapping: dict[str, int], return_type: Generic[T]):
    _valid: dict[str: type] = get_annotations(return_type)
    for _attr, _type in _valid:
        if _attr not in mapping.keys():
            raise DataValidationError("%s attribute %s is missing from header %s", return_type.__name__, _attr, header)
        if (_error_type := type(data[mapping[_attr]])) != _type:
            raise DataValidationError(" %s attribute of type [%s] is mapped to data of type [%s], dtypes must match", return_type.__name__, _attr,  _type, _error_type) 

def read_positional_data(data: Tuple|List, header:  
