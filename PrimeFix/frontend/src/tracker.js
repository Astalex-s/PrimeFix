/**
 * Трекер поведенческих метрик пользователя.
 *
 * Собирает:
 *  - time_on_page_seconds — секунды на странице
 *  - buttons_clicked      — JSON {текст_кнопки: кол-во}
 *  - cursor_hover_data    — JSON {"w", "h", "pts": [[x,y], ...]}
 *
 * Данные записываются в таблицу lead_metrics.
 * Первый запрос: POST /api/lead-metrics/ (создаёт запись, получает id).
 * Последующие:  PATCH /api/lead-metrics/{id}.
 */

// Не запускать внутри iframe (хитмэп-страница)
if (window === window.top) {
  (function () {
    'use strict';

    var API = '/api/lead-metrics';
    var TICK = 1000;

    var recordId = null;
    var timeOnPage = 0;
    var buttonsClicked = {};
    var cursorPoints = [];
    var lastX = 0;
    var lastY = 0;
    var sending = false;

    // ── Курсор ──────────────────────────────────────

    document.addEventListener('mousemove', function (e) {
      lastX = e.pageX;
      lastY = e.pageY;
    }, { passive: true });

    document.addEventListener('touchmove', function (e) {
      if (e.touches.length) {
        lastX = e.touches[0].pageX;
        lastY = e.touches[0].pageY;
      }
    }, { passive: true });

    // ── Клики ───────────────────────────────────────

    document.addEventListener('click', function (e) {
      var label = getLabel(e.target);
      if (label) buttonsClicked[label] = (buttonsClicked[label] || 0) + 1;
    }, true);

    function getLabel(el) {
      var node = el;
      for (var i = 0; i < 5 && node && node !== document.body; i++) {
        if (node.tagName === 'BUTTON' || node.tagName === 'A') {
          var t = (node.textContent || '').trim().substring(0, 60);
          return t || node.getAttribute('href') || node.tagName;
        }
        node = node.parentElement;
      }
      var tag = el.tagName.toLowerCase();
      return el.id ? tag + '#' + el.id : tag;
    }

    // ── Данные ──────────────────────────────────────

    function payload() {
      return {
        time_on_page_seconds: timeOnPage,
        buttons_clicked: JSON.stringify(buttonsClicked),
        cursor_hover_data: JSON.stringify({
          w: document.documentElement.scrollWidth || window.innerWidth,
          h: document.documentElement.scrollHeight || window.innerHeight,
          pts: cursorPoints,
        }),
        return_count: 0,
      };
    }

    // ── Отправка ────────────────────────────────────

    function send() {
      if (sending) return;
      sending = true;
      var url = recordId === null ? API + '/' : API + '/' + recordId;
      var method = recordId === null ? 'POST' : 'PATCH';

      fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload()),
      })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { if (d && d.id && !recordId) recordId = d.id; })
        .catch(function () {})
        .finally(function () { sending = false; });
    }

    function sendFinal() {
      var data = payload();
      if (recordId) {
        fetch(API + '/' + recordId, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
          keepalive: true,
        }).catch(function () {});
      } else if (navigator.sendBeacon) {
        navigator.sendBeacon(API + '/', new Blob([JSON.stringify(data)], { type: 'application/json' }));
      }
    }

    // ── Тик каждую секунду ──────────────────────────

    var timer = setInterval(function () {
      timeOnPage++;
      cursorPoints.push([Math.round(lastX), Math.round(lastY)]);
      send();
    }, TICK);

    window.addEventListener('beforeunload', function () { clearInterval(timer); sendFinal(); });
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') sendFinal();
    });
  })();
}
