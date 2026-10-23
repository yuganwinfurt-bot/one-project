from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class CustomerAfterSaleCreate(BaseModel):
    service_type: Literal["refund", "return", "exchange"]
    reason: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    exchange_address_id: int | None = Field(default=None, ge=1)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("请填写申请原因")
        return value

    @field_validator("description")
    @classmethod
    def strip_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_return_details(self):
        if self.service_type == "exchange" and not self.exchange_address_id:
            raise ValueError("换货申请请选择新的收货地址")
        if self.service_type != "exchange" and self.exchange_address_id is not None:
            raise ValueError("只有换货申请需要选择新的收货地址")
        return self


class AfterSaleReturnShipmentUpdate(BaseModel):
    return_tracking_no: str = Field(min_length=1, max_length=100)

    @field_validator("return_tracking_no")
    @classmethod
    def strip_tracking_no(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("请填写寄回物流单号")
        return value


class CustomerAfterSaleServiceRating(BaseModel):
    rating: int = Field(ge=1, le=5)
    feedback: str | None = Field(default=None, max_length=1000)

    @field_validator("feedback")
    @classmethod
    def strip_feedback(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AfterSaleExchangeShipmentUpdate(BaseModel):
    exchange_tracking_no: str = Field(min_length=1, max_length=100)

    @field_validator("exchange_tracking_no")
    @classmethod
    def strip_tracking_no(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("请填写换货商品的物流单号")
        return value


class AfterSaleProcess(BaseModel):
    action: Literal["approve", "reject", "complete"]
    admin_note: str | None = Field(default=None, max_length=2000)

    @field_validator("admin_note")
    @classmethod
    def strip_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AfterSaleMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("消息内容不能为空")
        return value
