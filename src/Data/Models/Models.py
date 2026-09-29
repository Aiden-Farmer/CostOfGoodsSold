from typing import NamedTuple
from datetime import datetime
from enum import Enum, auto
from decimal import Decimal

class SupportedSalesChannels(Enum):
    Shopify = auto()
    Amazon = auto()
    eBay = auto()
    Etsy = auto()
    Walmart = auto()
    Wayfair = auto()


class InventoryRecord(NamedTuple):
    """Inventory for single sku at a given date."""
    sku: str
    quantity: Decimal
    date: datetime


class SalesRecord(NamedTuple):
    """Sales transaction data container."""
    sku: str
    quantity: Decimal
    channel: SupportedSalesChannels


class PurchaseRecord(NamedTuple):
    """Purchase transaction data container."""
    sku: str
    quantity: Decimal


class TransferRecord(NamedTuple):
    """Inventory Transfer record."""
    from_sku: str
    to_sku: str
    quantity: Decimal
    date: datetime

