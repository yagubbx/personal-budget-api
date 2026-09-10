# Personal Budget API

FastAPI, SQLAlchemy 2 və PostgreSQL ilə hazırlanmış şəxsi büdcə və xərc idarəetmə REST API-si.

## Layihənin imkanları

- Gəlir və xərc əməliyyatı əlavə etmək
- Bütün əməliyyatları siyahılamaq
- Əməliyyatları tarix aralığına və növə görə filtrləmək
- Ümumi gəlir, ümumi xərc və cari balansı hesablamaq
- Pydantic ilə daxil edilən məlumatları yoxlamaq
- PostgreSQL-də məlumatları daimi saxlamaq
- Proqram başladıqda `transactions` cədvəlini avtomatik yaratmaq
- Swagger UI və avtomatik testlər vasitəsilə yoxlamaq

## Qovluq quruluşu

```text
personal-budget-api/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── budget.py
│   │   └── transactions.py
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requests.http
├── requirements.txt
└── README.md
```

## 1. Lazım olan proqramlar

Windows kompüterdə bunlar olmalıdır:

1. Python 3.11 və ya daha yeni versiya
2. Visual Studio Code
3. PostgreSQL və pgAdmin 4

Docker istifadə etmək məcburi deyil. Kompüterdə Docker yoxdursa, aşağıdakı əsas PostgreSQL üsulundan istifadə et.

## 2. Layihəni VS Code-da açmaq

ZIP faylını çıxart. Alınan `personal-budget-api` qovluğuna sağ klik edib **Open with Code** seç.

Bu seçim görünmürsə:

1. VS Code-u aç.
2. **File > Open Folder** seç.
3. `personal-budget-api` qovluğunu göstər.
4. Yuxarıdakı menyudan **Terminal > New Terminal** aç.

Terminalın əvvəlində yolun `personal-budget-api` ilə bitdiyinə əmin ol.

## 3. Virtual mühit yaratmaq

VS Code terminalında aşağıdakı əmrləri bir-bir icra et:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Əgər PowerShell aktivləşdirmə əmrinə icazə vermirsə, əvvəl bunu yaz:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Aktiv olduqda terminal sətrinin əvvəlində `(.venv)` görünəcək.

VS Code Python interpreter soruşsa, `.venv` olan variantı seç. Özün seçmək üçün `Ctrl+Shift+P`, sonra **Python: Select Interpreter**, daha sonra `.venv` seç.

## 4. PostgreSQL bazasını yaratmaq

### pgAdmin vasitəsilə

1. **pgAdmin 4** proqramını aç.
2. Sol tərəfdə **Servers > PostgreSQL** hissəsini genişləndir.
3. Quraşdırma zamanı verdiyin PostgreSQL parolunu daxil et.
4. **Databases** üzərində sağ klik et.
5. **Create > Database** seç.
6. Database sahəsinə `budget_db` yaz.
7. **Save** düyməsini bas.

Bazanın özünü əvvəlcədən yaradırıq. API başladıqda isə onun daxilindəki `transactions` cədvəli avtomatik yaranacaq.

### Alternativ: Query Tool vasitəsilə

pgAdmin-da serveri seç, **Tools > Query Tool** aç və bunu icra et:

```sql
CREATE DATABASE budget_db;
```

Əgər bazanı pgAdmin ilə artıq yaratmısansa, bu SQL-i ikinci dəfə işlətmə.

## 5. `.env` faylını yaratmaq

VS Code terminalında:

```powershell
Copy-Item .env.example .env
```

Sonra sol tərəfdə yaranmış `.env` faylını aç. İçində bu olacaq:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/budget_db
```

İkinci `postgres` sözünü PostgreSQL quraşdırarkən təyin etdiyin real parolla dəyiş:

```env
DATABASE_URL=postgresql+psycopg://postgres:SENIN_PAROLUN@localhost:5432/budget_db
```

`.env` faylını GitHub-a göndərmə. `.gitignore` artıq bunun qarşısını alır.

Parolda `@`, `:`, `/`, `#` kimi xüsusi işarələr varsa, bağlantı sətrində kodlaşdırılmalıdır. Vaxt itirməmək üçün lokal dərs layihəsində hərf və rəqəmlərdən ibarət parol istifadə etmək daha rahatdır.

## 6. API-ni işə salmaq

Virtual mühit aktiv olan terminalda:

```powershell
uvicorn app.main:app --reload
```

Uğurlu nəticədə təxminən belə ünvan görünəcək:

```text
Uvicorn running on http://127.0.0.1:8000
```

Terminalı bağlama. Brauzerdə bunu aç:

```text
http://127.0.0.1:8000/docs
```

Serveri dayandırmaq üçün terminalda `Ctrl+C` bas.

## 7. Swagger UI ilə bütün endpoint-ləri yoxlamaq

### POST `/transactions/` — gəlir əlavə etmək

1. `/docs` səhifəsində `POST /transactions/` sətrini aç.
2. **Try it out** seç.
3. Bu JSON-u yaz:

```json
{
  "amount": 1500.00,
  "type": "income",
  "category": "Salary"
}
```

4. **Execute** bas.
5. Status kodu `201 Created` olmalıdır.

Xərc nümunəsi:

```json
{
  "amount": 45.90,
  "type": "expense",
  "category": "Food"
}
```

Burada `type` yalnız `income` və ya `expense` ola bilər.

### GET `/transactions/` — əməliyyatları almaq

Filtrsiz sorğu bütün əməliyyatları ən yenidən ən köhnəyə qaytarır.

Filtrləmə nümunələri:

```text
GET /transactions/?type=expense
GET /transactions/?start_date=2026-09-01&end_date=2026-09-30
GET /transactions/?type=income&start_date=2026-09-01&end_date=2026-09-30
```

Tarix formatı `YYYY-MM-DD` olmalıdır. Başlanğıc tarixi bitmə tarixindən sonra olarsa API `400 Bad Request` qaytarır.

### GET `/budget/summary` — ümumi hesabat

Nümunə cavab:

```json
{
  "total_income": "1500.00",
  "total_expense": "45.90",
  "balance": "1454.10"
}
```

### Validation yoxlaması

POST sorğusunda mənfi məbləğ göndər:

```json
{
  "amount": -20,
  "type": "expense",
  "category": "Food"
}
```

API çökməməli və `422 Unprocessable Entity` qaytarmalıdır. Yanlış `type`, boş `category`, mətn tipli məbləğ və iki rəqəmdən çox qəpik hissəsi də validation xətası verir.

## 8. Avtomatik testləri işə salmaq

API işləyirsə əvvəl `Ctrl+C` ilə dayandır. Sonra:

```powershell
pytest -q
```

Gözlənilən nəticə:

```text
5 passed
```

Testlər real PostgreSQL məlumatlarına toxunmur. Onlar ayrıca, yaddaşda yaradılan müvəqqəti SQLite bazasından istifadə edir.

## 9. PostgreSQL-də yaranmış cədvələ baxmaq

1. pgAdmin-da `budget_db` bazasını tap.
2. **Schemas > public > Tables** aç.
3. Siyahıda `transactions` görünməlidir.
4. Cədvələ sağ klik et və **View/Edit Data > All Rows** seç.

Cədvəl görünmürsə **Tables** üzərində sağ klik edib **Refresh** et.

## 10. Docker olan kompüter üçün alternativ

Bu hissə yalnız Docker Desktop işləyirsə lazımdır. Lokal PostgreSQL istifadə etmisənsə, buranı keç.

```powershell
docker compose up -d db
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

`.env.example` faylındakı istifadəçi adı, parol, port və database adı `docker-compose.yml` ilə eynidir.

Konteyneri dayandırmaq:

```powershell
docker compose stop
```

Məlumatları da silmək istəsən:

```powershell
docker compose down -v
```

Sonuncu əmr Docker bazasındakı bütün layihə məlumatlarını silir.

## Faylların rolu

| Fayl | Vəzifəsi |
|---|---|
| `app/main.py` | FastAPI tətbiqini yaradır, router-ləri qoşur və startup zamanı cədvəli yaradır |
| `app/config.py` | `.env` daxilindəki konfiqurasiyanı oxuyur |
| `app/database.py` | SQLAlchemy engine, session və Base obyektlərini yaradır |
| `app/models.py` | PostgreSQL `transactions` cədvəlinin ORM modelini müəyyən edir |
| `app/schemas.py` | Request və response məlumatlarını Pydantic ilə yoxlayır |
| `app/routers/transactions.py` | POST, GET və filtrləmə əməliyyatlarını saxlayır |
| `app/routers/budget.py` | Ümumi gəlir, xərc və balans sorğusunu hesablayır |
| `tests/test_api.py` | Endpoint və validation davranışlarını avtomatik yoxlayır |

## Tez-tez rast gəlinən xətalar

### `py is not recognized`

Python quraşdırılmayıb və ya PATH-ə əlavə edilməyib. Python-u quraşdırarkən **Add Python to PATH** seçimini aktiv et. Alternativ olaraq əmrlərdə `py` əvəzinə `python` yaz.

### `uvicorn is not recognized`

Virtual mühit aktiv deyil və ya paketlər quraşdırılmayıb:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Alternativ işə salma əmri:

```powershell
python -m uvicorn app.main:app --reload
```

### `password authentication failed for user postgres`

`.env` faylındakı parol PostgreSQL parolu ilə eyni deyil. Parolu düzəlt, serveri `Ctrl+C` ilə dayandır və yenidən başlat.

### `database budget_db does not exist`

pgAdmin-da `budget_db` bazasını yaratmamısan. 4-cü addımı yenidən et.

### `connection refused`

PostgreSQL xidməti işləmir. Windows axtarışında **Services** aç, adı `postgresql` ilə başlayan xidməti tap və **Start** seç.

### Port 8000 artıq istifadə olunur

Başqa port seç:

```powershell
uvicorn app.main:app --reload --port 8001
```

Bu halda Swagger ünvanı `http://127.0.0.1:8001/docs` olacaq.

## Müəllimə qısa izah

Sorğu əvvəlcə FastAPI endpoint-inə daxil olur. `TransactionCreate` sxemi məlumatı yoxlayır. Məlumat düzgündürsə SQLAlchemy ORM onu PostgreSQL-də `transactions` cədvəlinə yazır. GET endpoint-i SQLAlchemy `select` sorğusuna seçilən tarix və növ filtrlərini əlavə edir. Summary endpoint-i isə SQL səviyyəsində `SUM` və `CASE` istifadə edərək gəlir və xərcləri hesablayır. Database session hər sorğu üçün açılır və sorğu bitəndə bağlanır. Tətbiqin lifespan mərhələsində `create_all` çağırıldığı üçün mövcud olmayan cədvəllər avtomatik yaradılır.

