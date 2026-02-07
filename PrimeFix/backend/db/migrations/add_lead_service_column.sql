-- Добавить колонку "услуга" в таблицу заявок (если таблица уже была создана до этого).
-- Выполнить один раз при обновлении с старой версии БД:
--   docker compose exec postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB> -f - < backend/db/migrations/add_lead_service_column.sql

ALTER TABLE leads ADD COLUMN IF NOT EXISTS service VARCHAR(255);
