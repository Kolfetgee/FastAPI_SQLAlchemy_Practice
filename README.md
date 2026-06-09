# FastAPI SQLAlchemy Practice

Практический проект по переводу FastAPI-приложения с in-memory store на PostgreSQL через SQLAlchemy ORM.

## Что реализовано

- Подключение PostgreSQL через SQLAlchemy async engine.
- Настройки через `.env` и `pydantic-settings`.
- Alembic-миграция для таблиц `users` и `projects`.
- Асинхронные репозитории через `AsyncSession`.
- CRUD для пользователей.
- Auth flow через PostgreSQL:
  - регистрация;
  - логин;
  - refresh token;
  - получение текущего пользователя через dependency;
  - получение текущего пользователя через middleware.
- CRUD для проектов.
- Массовое создание проектов.
- Пагинация проектов.
- Фильтрация проектов по статусу и ответственному пользователю.
- Сортировка проектов.
- Обработка базовых ошибок:
  - duplicate key;
  - foreign key;
  - not found;
  - validation errors.

## Технологии

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pytest
- HTTPX / TestClient
- Uvicorn
- uv

## Структура проекта

```text
src/
  apps/
    auth/
      dependencies.py
      middleware.py
      routers.py
      schemas.py
      services.py
      utils.py
    project/
      models.py
      repository.py
      routers.py
      schemas.py
      services.py
    user/
      models.py
      repository.py
      routers.py
      schemas.py
      services.py
  db/
    base.py
    session.py
  settings/
    settings.py
  main.py

alembic/
  versions/

tests/
  conftest.py
  test_app.py
```

## Переменные окружения

Создать файл `.env` на основе `.env.example`.

Пример:

```env
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_sqlalchemy_db

JWT_SECRET_KEY=secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
```

## Установка зависимостей

```bash
uv sync
```

## Применение миграций

```bash
uv run alembic upgrade head
```

Проверить текущую миграцию:

```bash
uv run alembic current
```

## Запуск приложения

```bash
uv run uvicorn src.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Основные API endpoints

### Users

```text
GET    /users/
GET    /users/{user_id}
GET    /users/by-ids
POST   /users/
POST   /users/many
PUT    /users/{user_id}
DELETE /users/{user_id}
```

### Auth

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me-dep
GET  /auth/me-middleware
```

### Projects

```text
GET    /projects/
GET    /projects/{project_id}
POST   /projects/
POST   /projects/many
PATCH  /projects/{project_id}
DELETE /projects/{project_id}
```

## Примеры запросов

### Создание пользователя

```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "123456"
}
```

### Регистрация

```json
{
  "username": "authuser",
  "email": "authuser@example.com",
  "password": "123456"
}
```

### Логин

```json
{
  "email": "authuser@example.com",
  "password": "123456"
}
```

### Создание проекта

```json
{
  "name": "Project One",
  "description": "Project description",
  "status": "new",
  "person_in_charge_id": 1
}
```

### Получение проектов с пагинацией

```text
GET /projects/?limit=10&offset=0
```

### Фильтрация по статусу

```text
GET /projects/?status=new
```

### Фильтрация по ответственному пользователю

```text
GET /projects/?person_in_charge_id=1
```

### Сортировка

```text
GET /projects/?sort_by=create_time
```

Допустимые поля сортировки:

```text
id
create_time
start_time
complete_time
```

## Тесты

Запуск всех тестов:

```bash
uv run pytest -q
```

Текущий результат:

```text
23 passed
```

Тесты покрывают:

- User CRUD;
- batch user routes;
- Auth register/login/refresh;
- dependency auth flow;
- middleware auth flow;
- validation errors;
- Project CRUD;
- Project pagination/filtering/sorting;
- Project duplicate name;
- Project foreign key error;
- Project not found cases;
- запрет лишних полей при update.

## Примечания по реализации

- `UserRepository` и `ProjectRepository` работают через `AsyncSession`.
- FastAPI routes получают DB-сессию через `Depends(get_db)`.
- Auth больше не использует старый in-memory connector.
- Старый `auth/connector.py` удалён как неиспользуемый.
- Тесты очищают PostgreSQL-таблицы `projects` и `users` перед/после тестов через `TRUNCATE ... RESTART IDENTITY CASCADE`.

## Статус

Проект переведён на PostgreSQL и SQLAlchemy ORM.

Основные user, auth и project flows проверены через pytest.