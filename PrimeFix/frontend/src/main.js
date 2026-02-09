// Подключение трекера поведенческих метрик
import './tracker.js';

/**
 * Анимации при появлении в зоне видимости
 */
function initScrollAnimations() {
  const els = document.querySelectorAll('.animate-on-scroll');
  if (!els.length) return;
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
  );
  els.forEach((el) => observer.observe(el));
}
initScrollAnimations();

/**
 * Список услуг из API (id, name, description) — для показа описания при выборе.
 */
let servicesList = [];

/**
 * Загрузка услуг из БД (GET /api/services) и заполнение <select id="service">.
 * В конец добавляется пункт «Другое». При выборе услуги под полем показывается описание.
 */
async function loadServices() {
  const select = document.getElementById('service');
  const descEl = document.getElementById('service-description');
  if (!select) return;
  while (select.options.length > 1) select.remove(1);
  servicesList = [];
  try {
    const res = await fetch('/api/services');
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data)) {
        servicesList = data;
        data.forEach((s) => {
          const opt = document.createElement('option');
          opt.value = s.name;
          opt.textContent = s.name;
          select.appendChild(opt);
        });
      }
    }
  } catch (_) {}
  const other = document.createElement('option');
  other.value = 'Другое';
  other.textContent = 'Другое';
  select.appendChild(other);

  function updateDescription() {
    if (!descEl) return;
    const name = select.value;
    if (!name || name === 'Другое') {
      descEl.textContent = '';
      descEl.hidden = true;
      return;
    }
    const service = servicesList.find((s) => s.name === name);
    if (service && service.description) {
      descEl.textContent = service.description;
      descEl.hidden = false;
    } else {
      descEl.textContent = '';
      descEl.hidden = true;
    }
  }
  select.addEventListener('change', updateDescription);
  updateDescription();
}
loadServices();

/**
 * Отправка формы заявки на POST /api/leads/
 */
const form = document.getElementById('lead-form');
const submitBtn = document.getElementById('submit-btn');
const messageEl = document.getElementById('form-message');

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    messageEl.textContent = '';
    messageEl.className = 'form-message';

    const formData = new FormData(form);
    const body = {};
    for (const [key, value] of formData.entries()) {
      const v = typeof value === 'string' ? value.trim() : value;
      body[key] = v || null;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка…';

    try {
      const res = await fetch('/api/leads/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText || `Ошибка ${res.status}`);
      }

      messageEl.textContent = 'Заявка отправлена. Мы свяжемся с вами в ближайшее время.';
      messageEl.className = 'form-message success';
      form.reset();
    } catch (err) {
      messageEl.textContent = err.message || 'Не удалось отправить заявку. Попробуйте позже.';
      messageEl.className = 'form-message error';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Оформить заказ';
    }
  });
}
