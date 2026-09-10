from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, TransactionType
from app.schemas import TransactionCreate, TransactionResponse


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
) -> Transaction:
    transaction = Transaction(**transaction_data.model_dump())

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction could not be saved",
        ) from exc

    return transaction


@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    start_date: date | None = Query(default=None, description="YYYY-MM-DD"),
    end_date: date | None = Query(default=None, description="YYYY-MM-DD"),
    transaction_type: TransactionType | None = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
) -> list[Transaction]:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be later than end_date",
        )

    query = select(Transaction)

    if start_date:
        start_datetime = datetime.combine(start_date, time.min)
        query = query.where(Transaction.created_at >= start_datetime)

    if end_date:
        next_day = datetime.combine(end_date + timedelta(days=1), time.min)
        query = query.where(Transaction.created_at < next_day)

    if transaction_type:
        query = query.where(Transaction.type == transaction_type)

    query = query.order_by(Transaction.created_at.desc(), Transaction.id.desc())

    try:
        return list(db.scalars(query).all())
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transactions could not be retrieved",
        ) from exc

