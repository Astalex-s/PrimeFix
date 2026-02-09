/**
 * Хитмэп-визуализация поведенческих метрик.
 *
 * Загружает данные cursor_positions из /api/behavior-metrics/,
 * агрегирует все точки и рисует тепловую карту поверх iframe
 * с главной страницей сайта.
 */

const API_AUTH = '/api/auth/login';
const API_METRICS = '/api/behavior-metrics/';

// ── DOM-элементы ──────────────────────────────────────────────────────

const loginOverlay = document.getElementById('login-overlay');
const loginBtn = document.getElementById('login-btn');
const loginInput = document.getElementById('login-input');
const passwordInput = document.getElementById('password-input');
const loginError = document.getElementById('login-error');

const wrapper = document.getElementById('heatmap-wrapper');
const frame = document.getElementById('page-frame');
const canvas = document.getElementById('heatmap-canvas');
const ctx = canvas.getContext('2d');

const radiusSelect = document.getElementById('radius-select');
const opacitySelect = document.getElementById('opacity-select');
const refreshBtn = document.getElementById('refresh-btn');
const statsEl = document.getElementById('stats');

let token = sessionStorage.getItem('heatmap_token') || '';

// ── Авторизация ───────────────────────────────────────────────────────

function checkAuth() {
  if (token) {
    loginOverlay.classList.add('hidden');
    loadAndRender();
  }
}

loginBtn.addEventListener('click', async () => {
  loginError.textContent = '';
  const login = loginInput.value.trim();
  const password = passwordInput.value;
  if (!login || !password) {
    loginError.textContent = 'Введите логин и пароль';
    return;
  }
  try {
    const res = await fetch(API_AUTH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      loginError.textContent = err.detail || 'Ошибка авторизации';
      return;
    }
    const data = await res.json();
    token = data.access_token;
    sessionStorage.setItem('heatmap_token', token);
    loginOverlay.classList.add('hidden');
    loadAndRender();
  } catch {
    loginError.textContent = 'Ошибка сети';
  }
});

passwordInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') loginBtn.click();
});

// ── Загрузка данных и рендер ──────────────────────────────────────────

let allPoints = []; // {x, y, origW, origH}

async function loadAndRender() {
  try {
    const res = await fetch(API_METRICS + '?limit=1000', {
      headers: { Authorization: 'Bearer ' + token },
    });
    if (res.status === 401) {
      token = '';
      sessionStorage.removeItem('heatmap_token');
      loginOverlay.classList.remove('hidden');
      return;
    }
    if (!res.ok) return;

    const records = await res.json();

    allPoints = [];
    let totalSessions = 0;
    let totalSeconds = 0;

    records.forEach((rec) => {
      totalSessions++;
      totalSeconds += rec.time_on_page || 0;

      if (!rec.cursor_positions) return;

      let parsed;
      try {
        parsed = JSON.parse(rec.cursor_positions);
      } catch {
        return;
      }

      const w = parsed.w || 1920;
      const h = parsed.h || 5000;
      const pts = parsed.pts || [];

      pts.forEach((pt) => {
        if (Array.isArray(pt) && pt.length >= 2) {
          allPoints.push({
            xPct: pt[0] / w,  // процент от ширины документа
            yPct: pt[1] / h,  // процент от высоты документа
          });
        }
      });
    });

    statsEl.textContent =
      'Сессий: ' + totalSessions +
      ' | Точек: ' + allPoints.length +
      ' | Время: ' + Math.round(totalSeconds / 60) + ' мин';

    renderHeatmap();
  } catch {
    statsEl.textContent = 'Ошибка загрузки данных';
  }
}

// ── Подстройка размеров под iframe ────────────────────────────────────

function syncCanvasSize() {
  try {
    const doc = frame.contentDocument || frame.contentWindow.document;
    const h = doc.documentElement.scrollHeight || doc.body.scrollHeight;
    frame.style.height = h + 'px';
    canvas.width = frame.offsetWidth;
    canvas.height = h;
    canvas.style.width = frame.offsetWidth + 'px';
    canvas.style.height = h + 'px';
  } catch {
    // Cross-origin fallback
    canvas.width = frame.offsetWidth;
    canvas.height = frame.offsetHeight || 3000;
    canvas.style.width = canvas.width + 'px';
    canvas.style.height = canvas.height + 'px';
  }
}

frame.addEventListener('load', () => {
  syncCanvasSize();
  if (allPoints.length) renderHeatmap();
});

// ── Рендер тепловой карты ─────────────────────────────────────────────

function renderHeatmap() {
  syncCanvasSize();

  const radius = parseInt(radiusSelect.value, 10);
  const opacity = parseFloat(opacitySelect.value);
  const cw = canvas.width;
  const ch = canvas.height;

  if (!cw || !ch || !allPoints.length) return;

  // 1. Shadow canvas: рисуем альфа-блобы для каждой точки
  const shadow = document.createElement('canvas');
  shadow.width = cw;
  shadow.height = ch;
  const sCtx = shadow.getContext('2d');

  allPoints.forEach((pt) => {
    const x = pt.xPct * cw;
    const y = pt.yPct * ch;

    const grad = sCtx.createRadialGradient(x, y, 0, x, y, radius);
    grad.addColorStop(0, 'rgba(0,0,0,0.05)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    sCtx.fillStyle = grad;
    sCtx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
  });

  // 2. Читаем пиксели shadow canvas, маппим альфу в цвет
  const imageData = sCtx.getImageData(0, 0, cw, ch);
  const pixels = imageData.data;

  // Находим максимальную альфу для нормализации
  let maxAlpha = 0;
  for (let i = 3; i < pixels.length; i += 4) {
    if (pixels[i] > maxAlpha) maxAlpha = pixels[i];
  }
  if (maxAlpha === 0) maxAlpha = 1;

  // Цветовой градиент: синий -> голубой -> зелёный -> жёлтый -> красный
  const gradientColors = [
    [0, 0, 255],     // синий      0%
    [0, 200, 255],   // голубой   25%
    [0, 255, 0],     // зелёный   50%
    [255, 255, 0],   // жёлтый    75%
    [255, 0, 0],     // красный  100%
  ];

  for (let i = 0; i < pixels.length; i += 4) {
    const alpha = pixels[i + 3];
    if (alpha === 0) continue;

    const normalized = alpha / maxAlpha; // 0..1
    const color = interpolateColor(gradientColors, normalized);

    pixels[i] = color[0];
    pixels[i + 1] = color[1];
    pixels[i + 2] = color[2];
    pixels[i + 3] = Math.round(normalized * 255 * opacity);
  }

  // 3. Рисуем результат на основной canvas
  ctx.clearRect(0, 0, cw, ch);
  ctx.putImageData(imageData, 0, 0);
}

/**
 * Линейная интерполяция по массиву цветов.
 * t — значение от 0 до 1.
 */
function interpolateColor(colors, t) {
  const n = colors.length - 1;
  const i = Math.min(Math.floor(t * n), n - 1);
  const f = t * n - i;
  const c0 = colors[i];
  const c1 = colors[i + 1];
  return [
    Math.round(c0[0] + (c1[0] - c0[0]) * f),
    Math.round(c0[1] + (c1[1] - c0[1]) * f),
    Math.round(c0[2] + (c1[2] - c0[2]) * f),
  ];
}

// ── Обработчики UI ────────────────────────────────────────────────────

radiusSelect.addEventListener('change', renderHeatmap);
opacitySelect.addEventListener('change', renderHeatmap);
refreshBtn.addEventListener('click', loadAndRender);

window.addEventListener('resize', () => {
  syncCanvasSize();
  if (allPoints.length) renderHeatmap();
});

// ── Старт ─────────────────────────────────────────────────────────────

checkAuth();
