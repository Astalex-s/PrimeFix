-- Создание таблицы администраторов для авторизации в админ-панели
-- Таблица используется для хранения учетных данных администраторов и управления доступом

-- Удаление таблицы, если она существует (для пересоздания с новым полем email)
DROP TABLE IF EXISTS admins CASCADE;

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для быстрого поиска по логину и email
CREATE INDEX ix_admins_login ON admins(login);
CREATE INDEX ix_admins_email ON admins(email);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE admins IS 'Таблица администраторов для авторизации в админ-панели';
COMMENT ON COLUMN admins.id IS 'Уникальный идентификатор администратора';
COMMENT ON COLUMN admins.login IS 'Логин администратора (уникальный)';
COMMENT ON COLUMN admins.email IS 'Email администратора (уникальный)';
COMMENT ON COLUMN admins.password_hash IS 'Хеш пароля администратора (bcrypt)';
COMMENT ON COLUMN admins.is_active IS 'Флаг активности администратора';
COMMENT ON COLUMN admins.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN admins.updated_at IS 'Дата и время последнего обновления записи';

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_admins_updated_at BEFORE UPDATE ON admins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
