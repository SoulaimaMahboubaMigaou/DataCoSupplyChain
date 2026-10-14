
from pydantic import BaseModel, Field


class DeliveryFeatures(BaseModel):
    days_for_shipment_scheduled: float
    shipping_mode: str
    customer_segment: str
    market: str
    order_region: str
    order_country: str
    category_name: str
    department_name: str
    order_item_quantity: float = Field(gt=0)
    sales: float = Field(ge=0)
    order_item_discount: float = Field(ge=0)
    order_item_profit_ratio: float
    product_price: float = Field(ge=0)
    order_month: int = Field(ge=1, le=12)
    order_day_of_week: int = Field(ge=0, le=6)
    order_quarter: int = Field(ge=1, le=4)