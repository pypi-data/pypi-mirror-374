from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Any

from pydantic import BaseModel, ConfigDict


PayInRequestStatus = Literal["waiting", "canceled", "paid", "failed"]

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


class SuccessResponse(BaseModel):
    success: Literal[True] = True
    data: Any

    model_config = ConfigDict(extra="ignore")


