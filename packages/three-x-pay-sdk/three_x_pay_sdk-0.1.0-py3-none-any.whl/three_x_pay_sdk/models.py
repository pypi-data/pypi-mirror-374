from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class PayInRequestStatus(str, Enum):
    waiting = "waiting"
    canceled = "canceled"
    paid = "paid"
    failed = "failed"


class CreatePayInRequest(BaseModel):
    amount: float
    currency: str
    merchant_order_id: str
    merchant_callback_url: Optional[str] = None
    merchant_return_url: Optional[str] = None
    is_test: bool

    model_config = ConfigDict(extra="ignore")


class PayInRequestSchema(BaseModel):
    id: int
    merchant_id: int
    status: PayInRequestStatus
    is_test: bool
    amount: float
    currency: str
    commission: float
    created_at: datetime
    payment_url: Optional[str] = None
    merchant_order_id: Optional[str] = None
    merchant_callback_url: Optional[str] = None
    merchant_return_url: Optional[str] = None
    failed_reason: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class SuccessResponsePayInRequest(BaseModel):
    success: Literal[True] = True
    data: PayInRequestSchema

    model_config = ConfigDict(extra="ignore")


