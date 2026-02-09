-- ═══════════════════════════════════════════════════════════════
-- Тестовые заявки (лиды) для проверки скоринга
-- 4 горячих  ·  3 тёплых  ·  3 холодных
-- У каждого горячего разные критерии «горячести»
-- ═══════════════════════════════════════════════════════════════

-- ──────────────────────────────────────────────────────────
-- HOT 1: Срочный дедлайн + крупный бюджет + ЛПР (директор)
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Алексей', 'Воронов', 'Игоревич',
  'Сеть автосервисов, 12 точек по Москве и МО, работаем 8 лет',
  'от 500 тыс. руб.',
  '+7 (916) 555-12-34',
  'Нужна срочная автоматизация всех точек до конца недели, готовы оплатить аванс сегодня',
  'Автосервис, автомобильный бизнес',
  '100+ сотрудников',
  'Комплексный проект на все 12 точек',
  'Генеральный директор',
  'крупный',
  'Постоянное обслуживание + разовая настройка',
  'Срочно, до конца этой недели',
  'Автоматизация и интеграция',
  'Обслуживание систем «умный дом»',
  'Telegram или звонок',
  'Любое время, вопрос срочный',
  'Обслуживание систем «умный дом»'
);

-- ──────────────────────────────────────────────────────────
-- HOT 2: Крупная компания + большой объём + владелец
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Марина', 'Соколова', 'Андреевна',
  'Строительный холдинг, 5 объектов одновременно в стройке',
  '1.2 млн руб.',
  'marina.s@stroiholding.ru',
  'Нужен полный технический аудит всех 5 объектов с отчётом для инвесторов',
  'Строительство, девелопмент',
  '500+ сотрудников',
  'Масштабный аудит 5 объектов',
  'Собственник',
  'крупный',
  'Регулярное обслуживание после аудита',
  '2 недели',
  'Технический аудит',
  'Технический аудит объекта',
  'Email',
  '10:00–18:00 по МСК',
  'Технический аудит объекта'
);

-- ──────────────────────────────────────────────────────────
-- HOT 3: Детально заполнено + срочность + средний бюджет
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Дмитрий', 'Петренко', NULL,
  'IT-компания, разработка ПО, офис 400 м², серверная комната',
  '200–300 тыс. руб.',
  '+7 (903) 789-00-11',
  'Серверная перегревается, нужен аварийный выезд и перенастройка кондиционирования ASAP',
  'IT, разработка ПО',
  '50 сотрудников',
  'Несколько систем требуют ревизии',
  'Руководитель IT-отдела',
  'средний',
  'Разовый выезд + договор на обслуживание',
  'ASAP, серверная перегревается',
  'Диагностика и ремонт',
  'Аварийный выезд специалиста',
  'Звонок',
  'Круглосуточно, ситуация аварийная',
  'Аварийный выезд специалиста'
);

-- ──────────────────────────────────────────────────────────
-- HOT 4: Высокий бюджет + ЛПР + конкретная потребность
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Ольга', 'Кравченко', 'Викторовна',
  'Ресторанный бизнес, 3 заведения в центре города, VIP-сегмент',
  'от 800 тыс. руб.',
  '+7 (926) 111-22-33',
  'Планируем полную модернизацию инженерных систем во всех 3 ресторанах. Бюджет согласован.',
  'HoReCa, ресторанный бизнес',
  '200+ сотрудников',
  'Крупный комплексный проект',
  'Управляющий партнёр',
  'крупный',
  'Постоянное сотрудничество',
  'В течение месяца начать, до конца квартала завершить',
  'Модернизация и обслуживание',
  'Плановое техническое обслуживание',
  'WhatsApp',
  '11:00–20:00',
  'Плановое техническое обслуживание'
);

-- ──────────────────────────────────────────────────────────
-- WARM 1: Средний бюджет + адекватный срок + менеджер
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Сергей', 'Новиков', 'Павлович',
  'Салон красоты премиум-класса',
  '100–200 тыс. руб.',
  '+7 (915) 444-55-66',
  'Хотим установить систему климат-контроля и «умный свет» в новом помещении',
  'Бьюти, услуги',
  '15 сотрудников',
  'Средний объём работ',
  'Менеджер по развитию',
  'малый',
  'Разовая установка',
  'В течение месяца',
  'Установка и настройка',
  'Обслуживание систем «умный дом»',
  'Telegram',
  '12:00–18:00',
  'Обслуживание систем «умный дом»'
);

-- ──────────────────────────────────────────────────────────
-- WARM 2: Конкретная услуга + небольшой бюджет + заполнено
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Елена', 'Федорова', 'Сергеевна',
  'Стоматологическая клиника, 3 кабинета',
  '80–120 тыс. руб.',
  'fedorova@dentclinic.ru',
  'Нужна диагностика вентиляции — пациенты жалуются на духоту',
  'Медицина, стоматология',
  '20 сотрудников',
  'Ряд работ по вентиляции',
  'Главный врач',
  'малый-средний',
  'Диагностика + возможно ремонт',
  '2-3 недели',
  'Диагностика',
  'Технический аудит объекта',
  'Email или звонок',
  '09:00–14:00',
  'Технический аудит объекта'
);

-- ──────────────────────────────────────────────────────────
-- WARM 3: Средний уровень, ищет информацию
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Артём', 'Белов', NULL,
  'Коворкинг-пространство на 80 рабочих мест',
  '50–100 тыс. руб.',
  '+7 (909) 321-00-99',
  NULL,
  'Коворкинг, аренда помещений',
  '10 сотрудников',
  'Несколько задач',
  'Руководитель проекта',
  'малый',
  'Разовая настройка',
  'Месяц',
  'Настройка оборудования',
  'Плановое техническое обслуживание',
  'Звонок',
  '10:00–17:00',
  'Плановое техническое обслуживание'
);

-- ──────────────────────────────────────────────────────────
-- COLD 1: Минимум данных
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Иван', 'Смирнов', NULL,
  NULL,
  NULL,
  '+7 (999) 000-11-22',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  'Другое'
);

-- ──────────────────────────────────────────────────────────
-- COLD 2: Мало данных, нет бюджета и дедлайна
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Анна', 'Козлова', NULL,
  'Маленький магазин',
  NULL,
  'anna_k@mail.ru',
  'Просто интересуюсь ценами',
  'Розничная торговля',
  NULL,
  NULL,
  NULL,
  'микро',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL
);

-- ──────────────────────────────────────────────────────────
-- COLD 3: Мало заполнено, неопределённые данные
-- ──────────────────────────────────────────────────────────
INSERT INTO leads (name, surname, patronymic, business_info, budget, contact_method,
  comments, niche, company_size, task_volume, role, business_size, need_volume,
  deadline, task_type, product_interest, preferred_contact_method, convenient_time, service)
VALUES (
  'Павел', 'Тихонов', 'Алексеевич',
  NULL,
  'пока не определён',
  '+7 (900) 123-45-67',
  'Пока изучаю рынок, может быть позже обратимся',
  NULL,
  '2-3 человека',
  NULL,
  'сотрудник',
  'микро',
  NULL,
  'Не определено',
  NULL,
  NULL,
  'Звонок',
  NULL,
  'Другое'
);
