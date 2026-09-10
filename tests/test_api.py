from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine)

    test_app = create_app(create_tables=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=test_engine)


def test_create_transaction(client: TestClient) -> None:
    response = client.post(
        "/transactions/",
        json={"amount": 1500, "type": "income", "category": "Salary"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["type"] == "income"
    assert data["category"] == "Salary"


def test_negative_amount_returns_422(client: TestClient) -> None:
    response = client.post(
        "/transactions/",
        json={"amount": -10, "type": "expense", "category": "Food"},
    )

    assert response.status_code == 422


def test_invalid_type_returns_422(client: TestClient) -> None:
    response = client.post(
        "/transactions/",
        json={"amount": 10, "type": "other", "category": "Test"},
    )

    assert response.status_code == 422


def test_filter_and_summary(client: TestClient) -> None:
    client.post(
        "/transactions/",
        json={"amount": 1000, "type": "income", "category": "Salary"},
    )
    client.post(
        "/transactions/",
        json={"amount": 250, "type": "expense", "category": "Rent"},
    )

    filtered = client.get("/transactions/?type=expense")
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["category"] == "Rent"

    summary = client.get("/budget/summary")
    assert summary.status_code == 200
    assert summary.json() == {
        "total_income": "1000.00",
        "total_expense": "250.00",
        "balance": "750.00",
    }


def test_wrong_date_range_returns_400(client: TestClient) -> None:
    response = client.get(
        "/transactions/?start_date=2026-09-10&end_date=2026-09-01"
    )

    assert response.status_code == 400

