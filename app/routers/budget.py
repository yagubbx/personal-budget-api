from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, TransactionType
from app.schemas import BudgetSummary


router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("/summary", response_model=BudgetSummary)
def get_budget_summary(db: Session = Depends(get_db)) -> BudgetSummary:
    summary_query = select(
        func.coalesce(
            func.sum(
                case(
                    (Transaction.type == TransactionType.INCOME, Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("total_income"),
        func.coalesce(
            func.sum(
                case(
                    (Transaction.type == TransactionType.EXPENSE, Transaction.amount),
                    else_=0,
                )
            ),
            0,
        ).label("total_expense"),
    )

    try:
        result = db.execute(summary_query).one()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Budget summary could not be calculated",
        ) from exc

    total_income = Decimal(result.total_income)
    total_expense = Decimal(result.total_expense)

    return BudgetSummary(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
    )

