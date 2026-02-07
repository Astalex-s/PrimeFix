# PrimeFix — Сервис сбора заявок

Безопасный стек для сбора заявок от клиентов. Данные хранятся только на сервере, доступ к API — через Nginx.

---

## Описание сервиса

PrimeFix — веб-сервис для приёма и хранения заявок от клиентов. Пользователь заполняет форму на сайте (имя, услуга, контакты, бюджет и т.п.), заявка сохраняется в PostgreSQL. Администратор управляет услугами и настройками через API, просматривает заявки в pgAdmin или через API.

**Основные возможности:**
- Форма заявки на сайте с выбором услуги и описанием
- CRUD API для заявок (leads), услуг (services), метрик поведения (lead_metrics), админ-настроек
- Публичный список услуг для выбора в форме
- Панель администратора (страница входа — в разработке)
- Локальный Docker Registry для обновления образа бэкенда

---

## Архитектура приложения

### Структура проекта

```
PrimeFix/
├── backend/                 # FastAPI (Python)
│   ├── core/                # Конфигурация, БД
│   ├── leads/               # Домен заявок (model, repository, schema, router)
│   ├── lead_metrics/        # Домен метрик поведения лида
│   ├── services/            # Домен услуг (публичный API + админ CRUD)
│   ├── admin/               # Домен админ-настроек (key-value)
│   ├── db/migrations/       # SQL-миграции
│   └── main.py              # Точка входа
├── frontend/                # Сайт (Vite, vanilla JS)
│   ├── index.html           # Главная страница + форма заявки
│   └── admin/               # Страница администратора
├── nginx/                   # Конфигурация обратного прокси
├── scripts/                 # Утилиты (create-registry-user, upgrade-docker)
└── docker-compose.yml
```

### Компоненты стека

| Сервис   | Описание                                      | Порты           |
|----------|-----------------------------------------------|-----------------|
| nginx    | Обратный прокси, статика, `/api/` → backend   | 80              |
| backend  | FastAPI, заявки и метрики                     | только внутри   |
| postgres | База данных                                   | только внутри   |
| pgadmin  | Веб-интерфейс БД                              | 5050            |
| registry | Docker Registry для образов бэкенда           | 5000            |
| watchtower | Автообновление образов                      | —               |

### API (префикс `/api`)

| Endpoint                 | Описание                         |
|--------------------------|----------------------------------|
| `GET /api/health`        | Проверка работы сервиса          |
| `POST /api/leads/`       | Создание заявки                  |
| `GET /api/leads/`        | Список заявок                    |
| `GET /api/services/`     | Публичный список услуг (форма)   |
| `GET/POST/PATCH/DELETE /api/admin/services/` | CRUD услуг              |
| `GET/POST/PATCH/DELETE /api/admin/`          | CRUD настроек           |
| `POST/GET /api/lead-metrics/{lead_id}` | Метрики поведения лида  |

---

## Быстрый старт

### Требования

- Docker с API 1.44+
- Docker Compose v2+

### Запуск

```bash
cd PrimeFix
docker compose up -d
```

Сайт: **http://localhost** (или IP/домен сервера). Админка: **http://localhost/admin**

### Обновление фронтенда после изменений

```bash
docker compose build nginx && docker compose up -d nginx
```

### Остановка

```bash
docker compose down          # без удаления данных
docker compose down -v       # с удалением volumes
```

---

## Конфигурация

### Переменные окружения

Параметры задаются в `.env` или в окружении. Основные:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — подключение к БД
- `PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD` — pgAdmin
- `REGISTRY_HTTP_SECRET` — секрет реестра (сменить в продакшене)

### Услуги в форме заявки

Услуги хранятся в таблице `services`. Добавление через API:

```bash
curl -X POST http://localhost/api/admin/services/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Консультация", "description": "Разовая консультация"}'
```

### Миграции БД

При первом старте таблицы создаются автоматически. Для старых БД:

```bash
docker compose exec -T postgres psql -U "${POSTGRES_USER:-app_user}" -d "${POSTGRES_DB:-app_db}" -f - < backend/db/migrations/add_lead_service_column.sql
```

---

## Docker Registry

Реестр для хранения образов бэкенда (порт 5000).

### Создание пользователя

```bash
bash scripts/create-registry-user.sh
```

### Вход и отправка образа

```bash
docker login localhost:5000 -u myuser -p mypassword
docker tag primefix-backend:latest localhost:5000/backend:latest
docker push localhost:5000/backend:latest
```

---

## pgAdmin

- URL: `http://<хост>:5050`
- Учётные данные: см. `docker-compose.yml` (по умолчанию `admin@example.com` / `change_me`)

Подключение к PostgreSQL: Host `postgres`, Port `5432`, DB `app_db`, User `app_user`.

---

## Безопасность

- PostgreSQL и backend не проброшены наружу — доступ только внутри Docker-сети
- Наружу открыты: 80 (Nginx), 5000 (Registry), 5050 (pgAdmin)
- Секреты в `.env` — файл в `.gitignore`, не коммитится

---

## Возможные расширения

- **Авторизация администратора** — вход через JWT или сессии, учётные данные в `admin_settings`
- **Уведомления** — email/Telegram при новой заявке
- **Экспорт заявок** — CSV/Excel через API
- **Метрики и аналитика** — дашборд по заявкам, конверсии, источникам
- **Кастомные поля заявки** — настройка полей через админку
- **Валидация и антиспам** — reCAPTCHA, ограничение частоты запросов
- **Многоязычность** — интерфейс и форма на разных языках

---

## Устранение неполадок

### Nginx: «host not found in upstream "backend"»

Убедитесь, что в `nginx/conf.d/default.conf` используется `resolver 127.0.0.11` и `proxy_pass http://$backend_ups`.

### Watchtower: «client version 1.25 is too old»

Нужен Docker API 1.44+. Обновление (Ubuntu/Debian):

```bash
sudo bash scripts/upgrade-docker.sh
```
