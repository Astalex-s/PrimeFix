/**
 * Трекер поведенческих метрик пользователя.
 *
 * Собирает:
 *  - time_on_page  — количество секунд на странице
 *  - buttons_clicked — JSON-объект {текст_кнопки: количество_кликов}
 *  - cursor_positions — JSON: {"w": ширина, "h": высота, "pts": [[x,y], ...]}
 *
 * Каждую секунду отправляет накопленные данные на бэкенд:
 *  - первый запрос: POST /api/behavior-metrics/ (создаёт запись, получает id)
 *  - последующие:  PATCH /api/behavior-metrics/{id} (обновляет запись)
 */
(function () {
  'use strict';

  const API_BASE = '/api/behavior-metrics';
  const TICK_MS = 1000;

  // ── Состояние трекера ───────────────────────────────────────────────

  let recordId = null;            // id записи в БД (после первого POST)
  let timeOnPage = 0;             // секунды на странице
  let buttonsClicked = {};        // {текст: количество}
  let cursorPoints = [];          // [[x, y], ...]
  let lastCursorX = 0;
  let lastCursorY = 0;
  let sending = false;            // защита от параллельных запросов

  // ── Слежение за курсором ────────────────────────────────────────────

  document.addEventListener('mousemove', function (e) {
    lastCursorX = e.pageX;
    lastCursorY = e.pageY;
  }, { passive: true });

  // Для тач-устройств
  document.addEventListener('touchmove', function (e) {
    if (e.touches.length > 0) {
      lastCursorX = e.touches[0].pageX;
      lastCursorY = e.touches[0].pageY;
    }
  }, { passive: true });

  // ── Слежение за кликами ─────────────────────────────────────────────

  document.addEventListener('click', function (e) {
    var target = e.target;
    var label = getClickLabel(target);
    if (label) {
      buttonsClicked[label] = (buttonsClicked[label] || 0) + 1;
    }
  }, true);

  /**
   * Получить читаемую метку кликнутого элемента.
   */
  function getClickLabel(el) {
    // Поднимаемся к ближайшей кнопке/ссылке
    var node = el;
    for (var i = 0; i < 5 && node && node !== document.body; i++) {
      if (node.tagName === 'BUTTON' || node.tagName === 'A') {
        var text = (node.textContent || '').trim().substring(0, 60);
        if (text) return text;
        if (node.href) return node.getAttribute('href');
        return node.tagName + (node.id ? '#' + node.id : '');
      }
      node = node.parentElement;
    }
    // Для любого другого элемента
    var tag = el.tagName.toLowerCase();
    if (el.id) return tag + '#' + el.id;
    if (el.className && typeof el.className === 'string') {
      return tag + '.' + el.className.split(/\s+/)[0];
    }
    return tag;
  }

  // ── Формирование данных ─────────────────────────────────────────────

  function buildPayload() {
    var docW = document.documentElement.scrollWidth || window.innerWidth;
    var docH = document.documentElement.scrollHeight || window.innerHeight;

    return {
      application_id: 0,
      time_on_page: timeOnPage,
      buttons_clicked: JSON.stringify(buttonsClicked),
      cursor_positions: JSON.stringify({
        w: docW,
        h: docH,
        pts: cursorPoints
      }),
      return_frequency: 0
    };
  }

  // ── Отправка данных ─────────────────────────────────────────────────

  function sendMetrics() {
    if (sending) return;
    sending = true;

    var payload = buildPayload();
    var url, method;

    if (recordId === null) {
      url = API_BASE + '/';
      method = 'POST';
    } else {
      url = API_BASE + '/' + recordId;
      method = 'PATCH';
    }

    fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        if (res.ok) return res.json();
        return null;
      })
      .then(function (data) {
        if (data && data.id && recordId === null) {
          recordId = data.id;
        }
      })
      .catch(function () {
        // Тихо игнорируем ошибки сети — трекер не должен мешать пользователю
      })
      .finally(function () {
        sending = false;
      });
  }

  /**
   * Финальная отправка при уходе со страницы (sendBeacon для надёжности).
   */
  function sendFinalMetrics() {
    var payload = buildPayload();

    if (recordId !== null) {
      // sendBeacon не поддерживает PATCH, используем POST с query-параметром
      // Бэкенд обработает как обычный PATCH через отдельный endpoint не нужен —
      // просто отправим через fetch с keepalive
      fetch(API_BASE + '/' + recordId, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(function () {});
    } else {
      // Если ещё не создали запись — попробуем через sendBeacon
      if (navigator.sendBeacon) {
        var blob = new Blob([JSON.stringify(payload)], {
          type: 'application/json',
        });
        navigator.sendBeacon(API_BASE + '/', blob);
      }
    }
  }

  // ── Основной цикл (каждую секунду) ─────────────────────────────────

  var tickInterval = setInterval(function () {
    timeOnPage++;
    cursorPoints.push([Math.round(lastCursorX), Math.round(lastCursorY)]);
    sendMetrics();
  }, TICK_MS);

  // ── Отправка при уходе ──────────────────────────────────────────────

  window.addEventListener('beforeunload', function () {
    clearInterval(tickInterval);
    sendFinalMetrics();
  });

  // Для мобильных: visibilitychange
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
      sendFinalMetrics();
    }
  });
})();
