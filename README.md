# Personal Budget API

FastAPI və PostgreSQL ilə hazırlanmış şəxsi büdcə idarəetmə REST API-si.

## Funksiyalar

* Gəlir və xərc əlavə etmək
* Əməliyyatları siyahılamaq
* Tarix və əməliyyat növünə görə filtrləmək
* Ümumi gəlir, xərc və balansı hesablamaq
* Yanlış məlumatları Pydantic ilə yoxlamaq
* Məlumatları PostgreSQL bazasında saxlamaq

## İstifadə olunan texnologiyalar

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* Pytest

## Quraşdırma

Layihəni kompüterə endirdikdən sonra virtual mühit yaradın:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Lazım olan paketləri quraşdırın:

```powershell
pip install -r requirements.txt
```

`.env.example` faylından `.env` yaradın:

```powershell
Copy-Item .env.example .env
```

`.env` faylında PostgreSQL bağlantısını qeyd edin:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/budget_db
```

PostgreSQL-də `budget_db` adlı database yaradılmalıdır. `transactions` cədvəli tətbiq başladıqda avtomatik yaranır.

## Layihəni işə salmaq

```powershell
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## API endpoint-ləri

| Metod | Endpoint          | Təyinat                                          |
| ----- | ----------------- | ------------------------------------------------ |
| POST  | `/transactions/`  | Yeni gəlir və ya xərc əlavə edir                 |
| GET   | `/transactions/`  | Əməliyyatları və filtrlənmiş nəticələri qaytarır |
| GET   | `/budget/summary` | Ümumi gəlir, xərc və balansı qaytarır            |

Yeni əməliyyat nümunəsi:

```json
{
  "amount": 1500.00,
  "type": "income",
  "category": "Salary"
}
```

Filtrləmə nümunəsi:

```text
GET /transactions/?type=expense&start_date=2026-09-01&end_date=2026-09-30
```

`type` dəyəri yalnız `income` və ya `expense` ola bilər. Mənfi məbləğ və yanlış məlumat daxil edildikdə API uyğun xəta cavabı qaytarır.

## Testlər

```powershell
pytest -q
```