# PrimeFix — Сервис сбора заявок

Безопасный стек для приёма заявок от клиентов. Доступ к приложению и API — только через Nginx (порт 80).

---

## Описание сервиса

PrimeFix — веб-сервис для приёма и хранения заявок. Посетитель заполняет форму на сайте (имя, услуга, контакты, бюджет и т.п.); заявка сохраняется в PostgreSQL. Администратор входит в панель по логину/паролю (JWT), просматривает заявки с интеллектуальным анализом (скоринг), управляет услугами и при необходимости смотрит тепловую карту и метрики поведения.

**Основные возможности:**
- Форма заявки на сайте с выбором услуги и расширенными полями
- CRUD API для заявок (leads), услуг (services), метрик поведения (lead_metrics)
- Публичный список услуг для выбора в форме
- Панель администратора (отдельные страницы):
  - **Заявки** — список с скорингом (горячий/тёплый/холодный), пагинация по 10 строк, детали по клику
  - **Услуги** — CRUD услуг, пагинация по 10 строк
  - **Тепловая карта** — визуализация кликов по странице
- Авторизация администратора: JWT, регистрация первого админа при пустой БД
- Доступ к API и БД только изнутри Docker-сети; снаружи открыт только Nginx (порт 80)

---

## Архитектура приложения

### Структура проекта

```
PrimeFix/
├── backend/                 # FastAPI (Python)
│   ├── core/                # Конфигурация, БД
│   ├── auth/                # Авторизация администраторов (JWT, регистрация)
│   ├── leads/               # Заявки, скоринг лидов
│   ├── lead_metrics/       # Метрики поведения (трекер, хитмэп)
│   ├── services/            # Услуги (публичный API + админ CRUD)
│   ├── admin/               # (пустой — функционал admin_settings удалён)
│   ├── db/migrations/       # SQL и автоматические миграции
│   └── main.py              # Точка входа
├── frontend/                # Сайт (Vite, vanilla JS)
│   ├── index.html           # Главная страница + форма заявки
│   ├── admin/
│   │   ├── index.html       # Заявки (по умолчанию)
│   │   ├── services.html    # Услуги
│   │   └── heatmap.html     # Тепловая карта
│   └── src/                 # JS, CSS
├── nginx/                   # Обратный прокси
├── scripts/                 # Утилиты (registry, upgrade-docker)
└── docker-compose.yml
```

### Компоненты стека

| Сервис   | Описание                                      | Порты    |
|----------|-----------------------------------------------|----------|
| nginx    | Обратный прокси, статика, `/api/` → backend   | 80       |
| backend  | FastAPI, заявки, услуги, метрики, авторизация | только внутри сети |
| postgres | База данных                                   | только внутри сети |
| watchtower | Автообновление образов (опционально)        | —        |

pgAdmin и Docker Registry в текущем стеке отключены (при необходимости можно раскомментировать в `docker-compose.yml`).

### API (префикс `/api`)

| Endpoint | Описание |
|----------|----------|
| `GET /api/health` | Проверка работы сервиса |
| `POST /api/auth/login` | Вход администратора (JWT) |
| `POST /api/auth/register` | Регистрация первого администратора |
| `GET /api/auth/me` | Текущий администратор (JWT) |
| `POST /api/leads/` | Создание заявки |
| `GET /api/leads/` | Список заявок |
| `GET /api/leads/scored/` | Список заявок с скорингом (JWT), параметры `skip`, `limit` |
| `GET /api/services/` | Публичный список услуг |
| `GET/POST/PATCH/DELETE /api/admin/services/` | CRUD услуг (JWT) |
| `POST/PATCH /api/lead-metrics/` | Метрики поведения (трекер) |
| `GET/DELETE /api/lead-metrics/` | Список/удаление метрик (JWT) |

---

## Быстрый старт

### Требования

- Docker с API 1.44+
- Docker Compose v2+

### Запуск

```bash
cd PrimeFix
docker compose up -d --build
```

Сайт: **http://localhost** (или IP/домен сервера).  
Админка: **http://localhost/admin/** — по умолчанию открывается страница «Заявки». Услуги: **http://localhost/admin/services.html**. Тепловая карта: **http://localhost/admin/heatmap.html**.

При первом заходе в админку (если в БД нет администраторов) доступна регистрация; далее — только вход по логину и паролю.

### Обновление после изменений

```bash
cd PrimeFix
docker compose up -d --build
```

### Остановка

```bash
cd PrimeFix
docker compose down          # без удаления данных
docker compose down -v       # с удалением volumes
```

---

## Конфигурация

### Переменные окружения

Параметры задаются в `PrimeFix/.env`. Основные:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — подключение к БД
- Остальные (pgAdmin, Watchtower и т.д.) — при использовании соответствующих сервисов

### Добавление услуг

Услуги хранятся в таблице `services`. Добавление через админку (страница «Услуги») или через API с JWT:

```bash
curl -X POST http://localhost/api/admin/services/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT>" \
  -d '{"name": "Консультация", "description": "Разовая консультация"}'
```

### Миграции БД

При старте backend таблицы создаются автоматически (SQLAlchemy + скрипт в `backend/db/migrations.py`). Отдельные SQL-миграции в `backend/db/migrations/` при необходимости выполняются вручную.

---

## Docker Registry (опционально)

Реестр в текущем `docker-compose.yml` закомментирован. При раскомментировании:

- Создание пользователя: `bash scripts/create-registry-user.sh`
- Вход и пуш образа: `docker login localhost:5000 -u myuser -p mypassword`, затем `docker push localhost:5000/backend:latest`

---

## Безопасность

- PostgreSQL и backend не проброшены на хост — доступ только из Docker-сети (Nginx проксирует `/api/` на backend).
- Снаружи открыт только порт **80** (Nginx). pgAdmin и Registry по умолчанию отключены.
- Секреты в `.env`; файл в `.gitignore`, в репозиторий не попадает.

---

## Устранение неполадок

### Nginx: «host not found in upstream "backend"»

В `nginx/conf.d/default.conf` должны быть `resolver 127.0.0.11` и `proxy_pass http://$backend_ups`.

### Watchtower: «client version 1.25 is too old»

Требуется Docker API 1.44+. Для обновления (Ubuntu/Debian): `sudo bash scripts/upgrade-docker.sh`.
