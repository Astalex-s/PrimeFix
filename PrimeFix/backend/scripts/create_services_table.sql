-- Таблица услуг (каждая услуга — отдельная строка с названием и описанием).
-- Выполнить один раз, если таблица ещё не создана (create_all в приложении создаёт её при старте).

CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
