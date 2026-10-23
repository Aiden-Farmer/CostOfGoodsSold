from src.CostOfGoodsSold.Utils import RowReader, convert, _check_for_none, _cnv_datetime, _cnv_str, build_row, validate_mapping, Mapping

from src.CostOfGoodsSold.Models import SalesRecord, InventoryRecord, SupportedSalesChannels
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

class TestRowReader:
    def test_row_reader_returns_SalesRecords(self):
        mapping = {"sku": 0, "quantity": 1, "channel": 2}
        data = ["sku-1", "10", "Etsy"]        
        reader = RowReader(SalesRecord, mapping)
        output = reader(data)
       
        assert isinstance(output, SalesRecord)
        assert output.sku == "sku-1"
        assert output.quantity == Decimal(10)
        assert output.channel == SupportedSalesChannels.Etsy

    def test_row_reader_returns_InventoryRecords(self) -> None:
        mapping = {"sku": 0, "quantity": 1, "date": 2}
        data = ["sku-1", "10", "2025-01-01"]
        reader = RowReader(InventoryRecord, mapping)
        output = reader(data)


        assert isinstance(output, InventoryRecord)
        assert output.sku == "sku-1"
        assert output.quantity == Decimal(10)
        assert output.date == datetime(2025, 1, 1)


    def tests_inventory_row_reader_handles_mm_slash_dd_slash_yyyy_format(self):
        mapping = {"sku": 0, "quantity": 1, "date": 2}
        data = ["sku-1", "10", "01/01/2025"]
        reader = RowReader(InventoryRecord, mapping)
        output = reader(data)

        assert output.date == datetime(2025, 1, 1)


