from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, field_validator

NOTICE = "Pricing and availability are subject to final confirmation by TD SYNNEX at the time of order."
COUNTRIES = ["Jamaica", "Barbados", "Trinidad and Tobago", "Bahamas", "Dominican Republic", "Costa Rica", "Panama", "Colombia", "Mexico", "Brazil"]


class Requirement(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=160)
    mandatory: bool = True


class SearchRequest(BaseModel):
    category: str = Field(min_length=1, max_length=80)
    manufacturer_preference: str | None = Field(default=None, max_length=80)
    requirements: list[Requirement] = Field(default_factory=list, max_length=20)
    quantity: int = Field(default=1, ge=1, le=10000)
    country: str = Field(default="Jamaica", max_length=80)
    currency: Literal["USD", "JMD", "BBD", "TTD", "MXN", "BRL", "COP"] = "USD"
    maximum_unit_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    warranty_required: bool = False
    allow_exceptions: bool = False
    additional_notes: str | None = Field(default=None, max_length=1000)

    @field_validator("country")
    @classmethod
    def supported_country(cls, value: str) -> str:
        if value not in COUNTRIES:
            raise ValueError("Select a supported Caribbean or Latin American country")
        return value


class Product(BaseModel):
    product_id: str
    sku: str
    manufacturer_part_number: str | None = None
    manufacturer: str
    model: str | None = None
    product_name: str
    category: str
    description: str | None = None
    technical_specifications: dict[str, str] = Field(default_factory=dict)
    unit_price: Decimal | None = None
    currency: str
    requested_quantity: int = 1
    available_quantity: int | None = None
    warehouse: str | None = None
    fulfillment_region: str | None = None
    eligible_countries: list[str] | None = None
    estimated_delivery: date | None = None
    warranty: str | None = None
    lifecycle_status: str | None = None
    orderable: bool = False
    confidence_score: int = 0
    confidence_level: str = "Requires verification"
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    matched_requirements: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    data_source: str = "Mock data — not a distributor quote"
    pricing_timestamp: datetime | None = None
    inventory_timestamp: datetime | None = None
    rank: int | None = None
    extended_price: Decimal | None = None
    quantity_shortfall: int | None = None
    availability_status: str = "Not provided by distributor"


class SearchResponse(BaseModel):
    recommendations: list[Product]
    regional_verification: list[Product]
    lifecycle_verification: list[Product]
    notice: str = NOTICE
    retrieved_at: datetime


class QuoteMetadata(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    opportunity_reference: str = Field(default="", max_length=120)
    prepared_by: str = Field(min_length=1, max_length=120)
    quote_date: date
    validity_date: date
    target_country: str
    currency: str


class ExportRequest(BaseModel):
    metadata: QuoteMetadata
    products: list[Product] = Field(min_length=1, max_length=5)
    requirements: list[Requirement] = Field(default_factory=list)

