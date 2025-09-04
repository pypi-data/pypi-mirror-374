"""Brightsites API models."""

from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, Field


class _BaseModel(PydanticBaseModel, strict=True, extra="forbid"):
    """Base model for all Brightsites models."""


class PaginationMeta(_BaseModel):
    """Pagination metadata."""

    total: int
    offset: int
    limit: int


class PaginatedResponse(_BaseModel):
    """A paginated response."""

    meta: PaginationMeta


class OrderSummary(_BaseModel):
    """Short view of an order."""

    created_at: datetime = Field(strict=False)
    updated_at: datetime = Field(strict=False)
    order_id: int
    shipping_method: str
    tracking: str
    status: str
    customer: EmailStr


class OrdersList(PaginatedResponse):
    """A list of orders."""

    orders: list[OrderSummary]


class ProductSubOption(_BaseModel):
    """Sub options for a product."""

    id: int
    name: str
    sub_sku: str
    image_src: str | None
    price_modifier: str
    position: int
    product_option_id: int


class ProductSubOptionsList(_BaseModel):
    """A list of sub options."""

    sub_options: list[ProductSubOption]


class ProductOption(_BaseModel):
    """A option for a product."""

    id: int
    name: str
    friendly_name: str
    option_type: str
    price_modifier_type: str
    show_in_inventory: bool
    show_as_thumbs: bool
    include_in_images: bool
    required: bool
    multiple_quantity: bool
    position: int


class ProductOptionsList(_BaseModel):
    """A list of options for a product."""

    enabled: bool
    options: list[ProductOption]


class ProductCategory(_BaseModel):
    """Product category."""

    id: int
    name: str


class ProductVendor(_BaseModel):
    """Product vendor."""

    id: int
    name: str


class ProductInventory(_BaseModel):
    """Inventory information for a product."""

    id: int
    inventory: int
    trigger: int
    track: bool
    allow_negative: bool
    sub_sku: str
    sub_option_ids: list[int]


class ProductSummary(_BaseModel):
    """Short view of a product."""

    created_at: datetime = Field(strict=False)
    updated_at: datetime = Field(strict=False)
    id: int
    name: str
    sku: str
    internal_id: str | None
    origin_address_id: int | None
    new_product: bool
    new_expires_at: datetime | None = Field(strict=False)
    categories: list[ProductCategory]
    vendors: list[ProductVendor]
    active: bool


class ProductsList(PaginatedResponse):
    """A list of products."""

    products: list[ProductSummary]


class Product(_BaseModel):
    """A product."""

    id: int
    name: str
    sku: str
    sku_separator: str
    internal_id: str | None
    origin_address_id: int | None
    new_product: bool
    new_expires_at: datetime | None = Field(strict=False)
    base_price: str
    retail_price: str | None
    cost: str | None
    setup_charge: str | None
    minimum_order_quantity: int | None
    maximum_order_quantity: int | None
    weight: str | None
    width: str | None
    height: str | None
    length: str | None
    shipping_modifier: str | None
    meta_title: str | None
    meta_description: str | None
    meta_keywords: str | None
    custom_url: str | None
    description: str
    active: bool
    featured: bool
    tax_exempt: bool
    shipping_exempt: bool
    categories: list[ProductCategory]
    vendors: list[ProductVendor]
    options: list[ProductOption]
    sub_options: list[ProductSubOption]
    inventories: list[ProductInventory]
    enable_quantity_discount: bool
    related_products_type: str
    enable_related_products: bool
    enable_product_personalization: bool
    enable_inventory: bool
    enable_logo_locations: bool
    enable_product_options: bool
    primary_category_id: int
    vendor_inventory_enabled: bool
    inventory_vendor_id: int | None
    tax_code: str | None
    note: str | None
    created_at: datetime | None = Field(strict=False)
    updated_at: datetime | None = Field(strict=False)
