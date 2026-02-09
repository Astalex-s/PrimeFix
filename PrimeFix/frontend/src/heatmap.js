/**
 * Хитмэп-визуализация + дашборд для lead_metrics.
 */

const API_AUTH = '/api/auth/login';
const API_METRICS = '/api/lead-metrics/';

// ── DOM ──────────────────────────────────────────────────────────────

const loginOverlay = document.getElementById('login-overlay');
const loginBtn = document.getElementById('login-btn');
const loginInput = document.getElementById('login-input');
const passwordInput = document.getElementById('password-input');
const loginError = document.getElementById('login-error');

const frame = document.getElementById('page-frame');
const canvas = document.getElementById('heatmap-canvas');
const ctx = canvas.getContext('2d');

const radiusSelect = document.getElementById('radius-select');
const opacitySelect = document.getElementById('opacity-select');
const refreshBtn = document.getElementById('refresh-btn');

// Dashboard elements
const dSessions = document.getElementById('d-sessions');
const dPoints = document.getElementById('d-points');
const dTotalTime = document.getElementById('d-total-time');
const dTotalTimeSub = document.getElementById('d-total-time-sub');
const dAvgTime = document.getElementById('d-avg-time');
const dMaxTime = document.getElementById('d-max-time');
const dClicksBlock = document.getElementById('d-clicks-block');
const dClicks = document.getElementById('d-clicks');

let token = sessionStorage.getItem('heatmap_token') || '';
let allPoints = [];

// ── Auth ─────────────────────────────────────────────────────────────

function checkAuth() {
  if (token) { loginOverlay.classList.add('hidden'); loadAndRender(); }
}

loginBtn.addEventListener('click', async () => {
  loginError.textContent = '';
  const login = loginInput.value.trim();
  const pw = passwordInput.value;
  if (!login || !pw) { loginError.textContent = 'Введите логин и пароль'; return; }
  try {
    const r = await fetch(API_AUTH, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password: pw }),
    });
    if (!r.ok) { loginError.textContent = (await r.json().catch(() => ({}))).detail || 'Ошибка'; return; }
    token = (await r.json()).access_token;
    sessionStorage.setItem('heatmap_token', token);
    loginOverlay.classList.add('hidden');
    loadAndRender();
  } catch { loginError.textContent = 'Ошибка сети'; }
});
passwordInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') loginBtn.click(); });

// ── Load & render ────────────────────────────────────────────────────

async function loadAndRender() {
  try {
    const r = await fetch(API_METRICS + '?limit=1000', { headers: { Authorization: 'Bearer ' + token } });
    if (r.status === 401) { token = ''; sessionStorage.removeItem('heatmap_token'); loginOverlay.classList.remove('hidden'); return; }
    if (!r.ok) return;

    const records = await r.json();
    allPoints = [];

    let totalSessions = 0;
    let totalSeconds = 0;
    let maxSeconds = 0;
    const clicksAgg = {};

    records.forEach((rec) => {
      totalSessions++;
      const t = rec.time_on_page_seconds || 0;
      totalSeconds += t;
      if (t > maxSeconds) maxSeconds = t;

      // Aggregate clicks
      if (rec.buttons_clicked) {
        try {
          const c = JSON.parse(rec.buttons_clicked);
          for (const [k, v] of Object.entries(c)) { clicksAgg[k] = (clicksAgg[k] || 0) + v; }
        } catch {}
      }

      // Aggregate cursor points
      if (!rec.cursor_hover_data) return;
      let parsed;
      try { parsed = JSON.parse(rec.cursor_hover_data); } catch { return; }
      const w = parsed.w || 1920;
      const h = parsed.h || 5000;
      const pts = parsed.pts || [];
      pts.forEach((pt) => {
        if (Array.isArray(pt) && pt.length >= 2) {
          allPoints.push({ xPct: pt[0] / w, yPct: pt[1] / h });
        }
      });
    });

    // ── Dashboard ───────────────────
    dSessions.textContent = totalSessions;
    dPoints.textContent = allPoints.length.toLocaleString();
    dTotalTime.textContent = fmtTime(totalSeconds);
    dTotalTimeSub.textContent = totalSeconds + ' сек';
    dAvgTime.textContent = totalSessions ? fmtTime(Math.round(totalSeconds / totalSessions)) : '—';
    dMaxTime.textContent = fmtTime(maxSeconds);

    // Top clicks
    const sorted = Object.entries(clicksAgg).sort((a, b) => b[1] - a[1]).slice(0, 10);
    if (sorted.length) {
      dClicksBlock.style.display = '';
      dClicks.innerHTML = sorted.map(([k, v]) =>
        '<li>' + escHtml(k) + '<span class="count">' + v + '</span></li>'
      ).join('');
    } else {
      dClicksBlock.style.display = 'none';
    }

    renderHeatmap();
  } catch {
    dSessions.textContent = 'Ошибка';
  }
}

function fmtTime(sec) {
  if (sec < 60) return sec + ' сек';
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (m < 60) return m + ' мин ' + s + ' сек';
  const h = Math.floor(m / 60);
  return h + ' ч ' + (m % 60) + ' мин';
}

function escHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Canvas sync ──────────────────────────────────────────────────────

function syncSize() {
  try {
    const doc = frame.contentDocument || frame.contentWindow.document;
    const h = Math.max(doc.documentElement.scrollHeight, doc.body.scrollHeight);
    frame.style.height = h + 'px';
    canvas.width = frame.offsetWidth;
    canvas.height = h;
    canvas.style.width = frame.offsetWidth + 'px';
    canvas.style.height = h + 'px';
  } catch {
    canvas.width = frame.offsetWidth || 1200;
    canvas.height = 4000;
    canvas.style.width = canvas.width + 'px';
    canvas.style.height = canvas.height + 'px';
    frame.style.height = canvas.height + 'px';
  }
}

frame.addEventListener('load', () => {
  syncSize();
  // Повторяем после полной отрисовки страницы с задержкой
  setTimeout(() => { syncSize(); if (allPoints.length) renderHeatmap(); }, 500);
  setTimeout(() => { syncSize(); if (allPoints.length) renderHeatmap(); }, 2000);
});

// ── Heatmap rendering ────────────────────────────────────────────────

function renderHeatmap() {
  syncSize();
  const radius = parseInt(radiusSelect.value, 10);
  const intensity = parseFloat(opacitySelect.value);
  const cw = canvas.width;
  const ch = canvas.height;
  if (!cw || !ch || !allPoints.length) return;

  // 1. Shadow canvas — рисуем альфа-блобы
  const shadow = document.createElement('canvas');
  shadow.width = cw;
  shadow.height = ch;
  const sCtx = shadow.getContext('2d');

  // Альфа за точку: чем больше точек, тем меньше альфа, но не менее 0.03
  const alphaPerPoint = Math.max(0.03, Math.min(0.3, 30 / allPoints.length));

  allPoints.forEach((pt) => {
    const x = pt.xPct * cw;
    const y = pt.yPct * ch;
    const grad = sCtx.createRadialGradient(x, y, 0, x, y, radius);
    grad.addColorStop(0, 'rgba(0,0,0,' + alphaPerPoint + ')');
    grad.addColorStop(0.6, 'rgba(0,0,0,' + (alphaPerPoint * 0.4) + ')');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    sCtx.fillStyle = grad;
    sCtx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
  });

  // 2. Читаем пиксели и маппим альфу в цвет
  const imgData = sCtx.getImageData(0, 0, cw, ch);
  const px = imgData.data;

  let maxA = 0;
  for (let i = 3; i < px.length; i += 4) { if (px[i] > maxA) maxA = px[i]; }
  if (maxA === 0) maxA = 1;

  const colors = [
    [0, 0, 255],     // синий
    [0, 180, 255],   // голубой
    [0, 230, 120],   // бирюзово-зелёный
    [255, 240, 0],   // жёлтый
    [255, 140, 0],   // оранжевый
    [255, 0, 0],     // красный
  ];

  for (let i = 0; i < px.length; i += 4) {
    const a = px[i + 3];
    if (a < 2) { px[i + 3] = 0; continue; }  // убираем шум
    const t = a / maxA;
    const c = lerpColor(colors, t);
    px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2];
    px[i + 3] = Math.round(Math.min(1, t * 1.5) * 255 * intensity);
  }

  ctx.clearRect(0, 0, cw, ch);
  ctx.putImageData(imgData, 0, 0);
}

function lerpColor(colors, t) {
  const n = colors.length - 1;
  const i = Math.min(Math.floor(t * n), n - 1);
  const f = t * n - i;
  const a = colors[i], b = colors[i + 1];
  return [
    Math.round(a[0] + (b[0] - a[0]) * f),
    Math.round(a[1] + (b[1] - a[1]) * f),
    Math.round(a[2] + (b[2] - a[2]) * f),
  ];
}

// ── UI events ────────────────────────────────────────────────────────

radiusSelect.addEventListener('change', renderHeatmap);
opacitySelect.addEventListener('change', renderHeatmap);
refreshBtn.addEventListener('click', loadAndRender);
window.addEventListener('resize', () => { syncSize(); if (allPoints.length) renderHeatmap(); });

// ── Start ────────────────────────────────────────────────────────────

checkAuth();
