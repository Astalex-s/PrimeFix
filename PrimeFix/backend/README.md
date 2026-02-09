# PrimeFix Backend API

FastAPI-приложение для управления заявками (лидами), метриками поведения, услугами и администрированием.

## Структура проекта

```
backend/
  core/           # Конфигурация и подключение к БД
  db/             # Миграции (SQL-скрипты и автоматические)
  auth/           # Авторизация администраторов (JWT)
  admin/          # Админ-настройки (key-value)
  leads/          # Заявки (лиды)
  lead_metrics/   # Метрики поведения пользователя
  services/       # Справочник услуг (публичный + админ CRUD)
  main.py         # Точка входа приложения
```

## Запуск

```bash
docker compose build backend
docker compose up -d backend
```

API доступно по адресу `http://<host>/api/`. Документация Swagger: `/api/docs`.

---

## Эндпоинты

### Health Check

| Метод | URL | Авторизация |
|-------|-----|-------------|
| GET | `/api/health` | Нет |

**200 OK**
```json
{"status": "ok"}
```

---

### Авторизация (`/api/auth`)

#### POST `/api/auth/login` — Вход администратора

**Тело запроса:**
```json
{"login": "admin", "password": "secret"}
```

**200 OK** — успешный вход:
```json
{"access_token": "eyJhbGciOiJIUz...", "token_type": "bearer"}
```

**401 Unauthorized** — неверные учётные данные:
```json
{"detail": "Неверный логин или пароль"}
```

---

#### POST `/api/auth/register` — Регистрация первого администратора

Доступна только если в системе ещё нет администраторов.

**Тело запроса:**
```json
{
  "login": "admin",
  "email": "admin@example.com",
  "password": "secret123",
  "password_confirm": "secret123"
}
```

**200 OK** — администратор создан:
```json
{
  "id": 1,
  "login": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "created_at": "2026-02-09T12:00:00Z"
}
```

**403 Forbidden** — администраторы уже существуют:
```json
{"detail": "Регистрация недоступна. В системе уже есть администраторы."}
```

**400 Bad Request** — дублирование логина или email:
```json
{"detail": "Администратор с таким логином уже существует"}
```

---

#### GET `/api/auth/check-admin-exists` — Проверка наличия администраторов

**200 OK:**
```json
{"exists": true, "count": 1}
```

---

#### GET `/api/auth/me` — Текущий администратор (требуется JWT)

**200 OK:**
```json
{
  "id": 1,
  "login": "admin",
  "email": "admin@example.com",
  "is_active": true,
  "created_at": "2026-02-09T12:00:00Z"
}
```

**401 Unauthorized** — токен отсутствует или недействителен:
```json
{"detail": "Неверный токен авторизации"}
```

---

### Заявки (`/api/leads`)

#### POST `/api/leads/` — Создание заявки

**Тело запроса** (обязательные поля: `name`, `surname`):
```json
{
  "name": "Иван",
  "surname": "Петров",
  "budget": "50-100 тыс.",
  "service": "Технический аудит"
}
```

**200 OK:**
```json
{
  "id": 1,
  "name": "Иван",
  "surname": "Петров",
  "budget": "50-100 тыс.",
  "service": "Технический аудит",
  "created_at": "2026-02-09T12:00:00Z",
  "...": "остальные поля"
}
```

---

#### GET `/api/leads/` — Список заявок

Параметры: `skip` (по умолчанию 0), `limit` (по умолчанию 100).

**200 OK:** массив объектов `Lead`.

---

#### GET `/api/leads/{lead_id}` — Заявка по ID

**200 OK:** объект `Lead`.

**404 Not Found:**
```json
{"detail": "Lead not found"}
```

---

#### PATCH `/api/leads/{lead_id}` — Обновление заявки

**200 OK:** обновлённый объект `Lead`.

**404 Not Found:**
```json
{"detail": "Lead not found"}
```

---

#### DELETE `/api/leads/{lead_id}` — Удаление заявки

**204 No Content** — успешно удалено.

**404 Not Found:**
```json
{"detail": "Lead not found"}
```

---

### Метрики лида (`/api/lead-metrics`)

#### POST `/api/lead-metrics/{lead_id}` — Создание метрик

**Тело запроса:**
```json
{
  "time_on_page_seconds": "120",
  "buttons_clicked": "cta_1,cta_2",
  "return_count": 2
}
```

**200 OK:** объект `LeadMetrics`.

**400 Bad Request:**
```json
{"detail": "Metrics for this lead already exist"}
```

---

#### GET `/api/lead-metrics/` — Список всех метрик

**200 OK:** массив объектов `LeadMetrics`.

---

#### GET `/api/lead-metrics/{lead_id}` — Метрики лида по ID

**200 OK:** объект `LeadMetrics`.

**404 Not Found:**
```json
{"detail": "Lead metrics not found"}
```

---

#### PATCH `/api/lead-metrics/{lead_id}` — Обновление метрик

**200 OK:** обновлённый объект `LeadMetrics`.

**404 Not Found:**
```json
{"detail": "Lead metrics not found"}
```

---

#### DELETE `/api/lead-metrics/{lead_id}` — Удаление метрик

**204 No Content** — успешно удалено.

**404 Not Found:**
```json
{"detail": "Lead metrics not found"}
```

---

### Услуги — публичный API (`/api/services`)

#### GET `/api/services/` — Список услуг

**200 OK:**
```json
[
  {"id": 1, "name": "Технический аудит объекта", "description": "..."},
  {"id": 2, "name": "Плановое техническое обслуживание", "description": "..."}
]
```

---

### Услуги — админ API (`/api/admin/services`, требуется JWT)

#### GET `/api/admin/services/` — Список услуг (для админки)

Параметры: `skip`, `limit`.

**200 OK:** массив объектов `Service` с `created_at`.

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```

---

#### POST `/api/admin/services/` — Создание услуги

**Тело запроса:**
```json
{"name": "Новая услуга", "description": "Описание"}
```

**200 OK:** созданный объект `Service`.

---

#### GET `/api/admin/services/{service_id}` — Услуга по ID

**200 OK:** объект `Service`.

**404 Not Found:**
```json
{"detail": "Service not found"}
```

---

#### PATCH `/api/admin/services/{service_id}` — Обновление услуги

**200 OK:** обновлённый объект `Service`.

**404 Not Found:**
```json
{"detail": "Service not found"}
```

---

#### DELETE `/api/admin/services/{service_id}` — Удаление услуги

**204 No Content** — успешно удалено.

**404 Not Found:**
```json
{"detail": "Service not found"}
```

---

### Админ-настройки (`/api/admin/settings`, требуется JWT)

#### POST `/api/admin/settings/` — Создание настройки

**Тело запроса:**
```json
{"key": "budget_ranges", "value": "[\"до 50 тыс.\",\"50-100 тыс.\"]"}
```

**200 OK:** объект `AdminSetting`.

**400 Bad Request:**
```json
{"detail": "Setting with this key already exists"}
```

---

#### GET `/api/admin/settings/` — Список настроек

**200 OK:** массив объектов `AdminSetting`.

---

#### GET `/api/admin/settings/key/{key}` — Настройка по ключу

**200 OK:** объект `AdminSetting`.

**404 Not Found:**
```json
{"detail": "Setting not found"}
```

---

#### GET `/api/admin/settings/{setting_id}` — Настройка по ID

**200 OK:** объект `AdminSetting`.

**404 Not Found:**
```json
{"detail": "Setting not found"}
```

---

#### PATCH `/api/admin/settings/{setting_id}` — Обновление настройки

**200 OK:** обновлённый объект `AdminSetting`.

**404 Not Found:**
```json
{"detail": "Setting not found"}
```

---

#### DELETE `/api/admin/settings/{setting_id}` — Удаление настройки

**204 No Content** — успешно удалено.

**404 Not Found:**
```json
{"detail": "Setting not found"}
```
