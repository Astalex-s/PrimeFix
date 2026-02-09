"""Интеллектуальный анализ и скоринг лидов.

Каждый лид получает оценку 0–100 («температуру»):
  - 70–100  горячий  (срочно, крупный бюджет, ЛПР, дедлайн)
  - 40–69   тёплый   (средний бюджет, адекватные сроки)
  -  0–39   холодный (мало данных, низкий бюджет, нет срочности)

Возвращается словарь с рекомендациями: приоритет, нужен ли
персональный менеджер, рекомендуемый отдел и пояснение.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# ── Результат скоринга ───────────────────────────────────────────────

@dataclass
class LeadScore:
    score: int                    # 0–100
    temperature: str              # горячий / тёплый / холодный
    priority: str                 # высокий / средний / низкий
    needs_personal_manager: bool
    department: str               # продажи / консалтинг / поддержка
    summary: str                  # краткое пояснение


# ── Справочники для анализа ──────────────────────────────────────────

_URGENT_WORDS = [
    "срочн", "немедленн", "сегодня", "завтра", "asap", "1-2 дн",
    "пару дней", "эта недел", "ближайш", "как можно скор",
    "до конца недел", "экстренн",
]
_MEDIUM_DEADLINE = [
    "2 недел", "месяц", "в течение месяц", "2-3 недел",
    "до конца месяц", "3-4 недел",
]

_HIGH_BUDGET_PATTERNS = [
    (r"(\d[\d\s]*)\s*(млн|миллион)", 1_000_000),
    (r"от\s*(\d[\d\s]*00)\s*тыс", 500_000),
    (r"(\d[\d\s]*00)\s*[-–]\s*(\d+)\s*тыс", 300_000),
    (r"500\s*[-–—]", 500_000),
]
_MID_BUDGET_PATTERNS = [
    (r"100\s*[-–—]", 100_000),
    (r"(\d[\d\s]*0)\s*[-–]\s*(\d+)\s*тыс", 50_000),
    (r"от\s*50", 50_000),
]

_DECISION_MAKERS = [
    "директор", "генеральный", "ceo", "cto", "coo", "cfo",
    "собственник", "владелец", "основатель", "учредитель",
    "руководитель", "партнёр", "партнер", "зам. директор",
    "коммерческий директор", "управляющий",
]
_MIDDLE_ROLES = [
    "менеджер", "начальник", "руководитель отдел", "тимлид",
    "team lead", "руководитель проект",
]

_LARGE_COMPANY = [
    "крупн", "500+", "1000+", "100+", "корпорац", "холдинг",
    "более 100", "более 50", "50-100", "100-500",
]
_MEDIUM_COMPANY = [
    "средн", "20-50", "10-50", "50 сотрудник", "малый-средн",
]


# ── Основная функция скоринга ────────────────────────────────────────

def score_lead(lead) -> LeadScore:
    """Вычислить скоринг лида. lead — ORM-объект или dict-like."""
    g = _field  # shortcut

    points = 0
    reasons: list[str] = []

    # 1. Срочность дедлайна (0–25)
    deadline = g(lead, "deadline")
    if deadline:
        dl = deadline.lower()
        if _any_match(dl, _URGENT_WORDS):
            points += 25
            reasons.append("срочный дедлайн")
        elif _any_match(dl, _MEDIUM_DEADLINE):
            points += 12
            reasons.append("умеренный дедлайн")
        else:
            points += 5
            reasons.append("указан дедлайн")

    # 2. Бюджет (0–25)
    budget = g(lead, "budget")
    if budget:
        bl = budget.lower()
        if _any_pattern(bl, _HIGH_BUDGET_PATTERNS):
            points += 25
            reasons.append("крупный бюджет")
        elif _any_pattern(bl, _MID_BUDGET_PATTERNS):
            points += 14
            reasons.append("средний бюджет")
        elif any(w in bl for w in ("тыс", "руб", "₽", "$", "€", "бюджет")):
            points += 7
            reasons.append("бюджет указан")

    # 3. Роль заполняющего (0–15)
    role = g(lead, "role")
    if role:
        rl = role.lower()
        if _any_match(rl, _DECISION_MAKERS):
            points += 15
            reasons.append("ЛПР (лицо, принимающее решения)")
        elif _any_match(rl, _MIDDLE_ROLES):
            points += 8
            reasons.append("средний менеджмент")
        else:
            points += 3

    # 4. Размер компании (0–10)
    company = g(lead, "company_size") or g(lead, "business_size") or ""
    if company:
        cl = company.lower()
        if _any_match(cl, _LARGE_COMPANY):
            points += 10
            reasons.append("крупная компания")
        elif _any_match(cl, _MEDIUM_COMPANY):
            points += 5
            reasons.append("средняя компания")
        else:
            points += 2

    # 5. Объём задач / потребность (0–10)
    volume = g(lead, "task_volume") or g(lead, "need_volume") or ""
    if volume:
        vl = volume.lower()
        if any(w in vl for w in ("больш", "масштаб", "комплекс", "постоянн", "регулярн", "крупн")):
            points += 10
            reasons.append("большой объём")
        elif any(w in vl for w in ("средн", "несколько", "ряд")):
            points += 5
        else:
            points += 2

    # 6. Полнота заполнения (0–15)
    filled = sum(
        1 for f in [
            "business_info", "budget", "niche", "company_size", "task_volume",
            "role", "business_size", "need_volume", "deadline", "task_type",
            "product_interest", "contact_method", "preferred_contact_method",
            "convenient_time", "comments", "service",
        ]
        if g(lead, f)
    )
    fill_score = min(15, round(filled * 1.2))
    points += fill_score
    if filled >= 10:
        reasons.append("детально заполнена заявка")
    elif filled >= 5:
        reasons.append("заявка заполнена частично")

    # ── Финальная оценка ─────────────────────────────
    score = min(100, max(0, points))

    if score >= 70:
        temperature = "горячий"
        priority = "высокий"
    elif score >= 40:
        temperature = "тёплый"
        priority = "средний"
    else:
        temperature = "холодный"
        priority = "низкий"

    # Персональный менеджер
    needs_pm = score >= 60 or _any_match((role or "").lower(), _DECISION_MAKERS)

    # Рекомендуемый отдел
    department = _recommend_department(lead)

    summary = "; ".join(reasons) if reasons else "мало данных для анализа"

    return LeadScore(
        score=score,
        temperature=temperature,
        priority=priority,
        needs_personal_manager=needs_pm,
        department=department,
        summary=summary,
    )


# ── Вспомогательные функции ──────────────────────────────────────────

def _field(obj, name: str) -> str | None:
    """Получить поле из ORM-объекта или dict."""
    val = getattr(obj, name, None) if hasattr(obj, name) else obj.get(name)
    if val and isinstance(val, str) and val.strip():
        return val.strip()
    return None


def _any_match(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def _any_pattern(text: str, patterns: list[tuple]) -> bool:
    for pattern, _ in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def _recommend_department(lead) -> str:
    task = (_field(lead, "task_type") or "").lower()
    service = (_field(lead, "service") or "").lower()
    niche = (_field(lead, "niche") or "").lower()
    combined = f"{task} {service} {niche}"

    if any(w in combined for w in ("аудит", "консульт", "анализ", "стратег", "оптимиз")):
        return "консалтинг"
    if any(w in combined for w in ("обслуж", "ремонт", "поддерж", "сервис", "аварий", "технич")):
        return "техподдержка"
    return "продажи"
