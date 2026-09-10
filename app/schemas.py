from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import TransactionType


PositiveAmount = Annotated[
    Decimal,
    Field(gt=0, max_digits=12, decimal_places=2, examples=[125.50]),
]


class TransactionCreate(BaseModel):
    amount: PositiveAmount
    type: TransactionType
    category: str = Field(min_length=1, max_length=100, examples=["Salary"])

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("Category cannot be empty")
        return value


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    type: TransactionType
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BudgetSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal

