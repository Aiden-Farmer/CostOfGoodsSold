from src.CostOfGoodsSold.Data.Utils.Utils import RowReader, convert, _check_for_none, _cnv_datetime, _cnv_decimal, _cnv_int, _cnv_str, build_row, validate_mapping, DataValidationError


from src.CostOfGoodsSold.Data.Models.Models import SalesRecord, InventoryRecord, SupportedSalesChannels
from decimal import Decimal, InvalidOperation
from datetime import datetime
from types import NoneType
import pytest


class TestConverters:
    def test_cnv_str_raises_on_empty_str(self):
        empty_str = ""
        with pytest.raises(ValueError):
            _cnv_str(empty_str)

    def test_union_type_conversion_prefers_first_type_of_union(self):
        element = "some string"
        _type = str|int
        assert isinstance(convert(element, _type), str) 

    def test_union_type_conversion_returns_valid_second_type(self):
        element = "some string"
        _type = int|str
        assert isinstance( convert(element, _type), str)

    def test_union_type_conversion_returns_none_on_empty_string(self):
        element = ""
        _type = str|None
        assert isinstance(convert(element, _type), NoneType)


    def test_buncha_types_work(self):
        element = "valid string"
        _type = int|Decimal|float|datetime|str|None
        assert isinstance(convert(element, _type), str)

class TestBuildRow:
    def test_build_row_raises_dtype_error_on_bad_data(self):
        data = ["bad", "data", "", 2, 2.4]
        types = [str, Decimal, SupportedSalesChannels]
        with pytest.raises(InvalidOperation):
            build_row(data, types, SalesRecord)


class TestValidateMapping:
    def test_validate_mapping_raises_DataValidationError_on_bad_mapping(self):
        mapping = {"sku": 0, "quantity":1, "not_channel": 2}
        validate_mapping(SalesRecord, mapping)
