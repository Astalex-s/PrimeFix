/**
 * Страница администратора с авторизацией через JWT токен.
 */

const API_BASE = '/api';
const TOKEN_KEY = 'admin_token';

// Утилиты для работы с токеном
const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  remove: () => localStorage.removeItem(TOKEN_KEY),
};

// Проверка авторизации
function isAuthenticated() {
  return !!tokenStorage.get();
}

// API запросы
async function apiRequest(url, options = {}) {
  const token = tokenStorage.get();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Making authenticated request to:', url, 'with token length:', token.length);
  } else {
    console.warn('No token available for request:', url);
  }

  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      console.error('Unauthorized request to:', url, 'Status:', response.status);
      const errorText = await response.text();
      console.error('Error response:', errorText);
      
      // Не перезагружаем страницу сразу, если это запрос /auth/me после логина
      if (url === '/auth/me') {
        tokenStorage.remove();
        throw new Error('Ошибка авторизации. Токен недействителен.');
      }
      tokenStorage.remove();
      window.location.reload();
      return;
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Ошибка запроса' }));
      let message = 'Ошибка запроса';
      if (typeof error.detail === 'string') {
        message = error.detail;
      } else if (Array.isArray(error.detail)) {
        message = error.detail.map(e => e.msg || e.message || String(e)).join('; ');
      }
      throw new Error(message);
    }

    // 204 No Content (DELETE и другие операции без тела ответа)
    if (response.status === 204) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('Request error:', error);
    throw error;
  }
}

// Проверка наличия администраторов
async function checkAdminExists() {
  try {
    // Этот запрос не требует авторизации
    const response = await fetch(`${API_BASE}/auth/check-admin-exists`);
    if (!response.ok) return false;
    const data = await response.json();
    return data.exists;
  } catch (error) {
    console.error('Ошибка проверки администраторов:', error);
    return false;
  }
}

// Вход
async function login(login, password) {
  // Запрос логина без токена
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ login, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка входа' }));
    throw new Error(error.detail || 'Ошибка входа');
  }

  const data = await response.json();
  
  // Проверяем наличие токена в ответе
  if (!data.access_token) {
    console.error('No access_token in response:', data);
    throw new Error('Токен не получен от сервера');
  }
  
  tokenStorage.set(data.access_token);
  console.log('Token saved, length:', data.access_token.length);
  return data;
}

// Регистрация
async function register(login, email, password, passwordConfirm) {
  // Запрос регистрации без токена
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      login, 
      email, 
      password, 
      password_confirm: passwordConfirm 
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка регистрации' }));
    throw new Error(error.detail || 'Ошибка регистрации');
  }

  return await response.json();
}

// Инициализация страницы
async function init() {
  const loginForm = document.getElementById('admin-login-form');
  const registerButton = document.getElementById('register-button');
  const errorMessage = document.getElementById('error-message');
  const successMessage = document.getElementById('success-message');
  const adminPanel = document.getElementById('admin-panel');
  const loginSection = document.getElementById('login-section');

  // Если пользователь уже авторизован, показываем админ-панель
  if (isAuthenticated()) {
    try {
      const adminInfo = await apiRequest('/auth/me');
      showAdminPanel(adminInfo);
      return;
    } catch (error) {
      tokenStorage.remove();
      // Продолжаем показ формы входа
    }
  }

  // Проверяем наличие администраторов
  const adminExists = await checkAdminExists();
  const emailField = document.getElementById('email-field');
  const passwordConfirmField = document.getElementById('password-confirm-field');
  
  if (!adminExists && registerButton) {
    registerButton.style.display = 'block';
    // Показываем поля для регистрации
    if (emailField) emailField.style.display = 'block';
    if (passwordConfirmField) passwordConfirmField.style.display = 'block';
    // Делаем поля обязательными
    const emailInput = document.getElementById('admin-email');
    const passwordConfirmInput = document.getElementById('admin-password-confirm');
    if (emailInput) emailInput.required = true;
    if (passwordConfirmInput) passwordConfirmInput.required = true;
  } else if (registerButton) {
    registerButton.style.display = 'none';
    // Скрываем поля для регистрации
    if (emailField) emailField.style.display = 'none';
    if (passwordConfirmField) passwordConfirmField.style.display = 'none';
    // Убираем обязательность полей
    const emailInput = document.getElementById('admin-email');
    const passwordConfirmInput = document.getElementById('admin-password-confirm');
    if (emailInput) emailInput.required = false;
    if (passwordConfirmInput) passwordConfirmInput.required = false;
  }

  // Обработка формы входа
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideMessages();

      const loginInput = document.getElementById('admin-login');
      const passwordInput = document.getElementById('admin-password');
      const loginValue = loginInput.value.trim();
      const passwordValue = passwordInput.value;

      if (!loginValue || !passwordValue) {
        showError('Заполните все поля');
        return;
      }

      try {
        const loginResult = await login(loginValue, passwordValue);
        console.log('Login successful, token saved');
        
        // Небольшая задержка для гарантии сохранения токена
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Проверяем, что токен сохранен
        const savedToken = tokenStorage.get();
        if (!savedToken) {
          throw new Error('Токен не был сохранен');
        }
        console.log('Token retrieved from storage, length:', savedToken.length);
        
        // Делаем запрос /auth/me с токеном
        try {
          const adminInfo = await apiRequest('/auth/me');
          console.log('Admin info received:', adminInfo);
          showAdminPanel(adminInfo);
        } catch (meError) {
          console.error('Error getting admin info:', meError);
          showError('Ошибка получения информации об администраторе: ' + meError.message);
          // Не очищаем токен, возможно проблема временная
        }
      } catch (error) {
        console.error('Login error:', error);
        showError(error.message || 'Ошибка входа');
      }
    });
  }

  // Обработка кнопки регистрации
  if (registerButton) {
    registerButton.addEventListener('click', async () => {
      hideMessages();
      
      const loginInput = document.getElementById('admin-login');
      const emailInput = document.getElementById('admin-email');
      const passwordInput = document.getElementById('admin-password');
      const passwordConfirmInput = document.getElementById('admin-password-confirm');
      
      const loginValue = loginInput.value.trim();
      const emailValue = emailInput.value.trim();
      const passwordValue = passwordInput.value;
      const passwordConfirmValue = passwordConfirmInput.value;

      if (!loginValue || !emailValue || !passwordValue || !passwordConfirmValue) {
        showError('Заполните все поля');
        return;
      }

      // Валидация email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(emailValue)) {
        showError('Введите корректный email адрес');
        return;
      }

      if (passwordValue.length < 6) {
        showError('Пароль должен содержать минимум 6 символов');
        return;
      }

      if (passwordValue !== passwordConfirmValue) {
        showError('Пароли не совпадают');
        return;
      }

      try {
        await register(loginValue, emailValue, passwordValue, passwordConfirmValue);
        showSuccess('Регистрация успешна! Выполняется вход...');
        // После регистрации автоматически входим
        setTimeout(async () => {
          try {
            await login(loginValue, passwordValue);
            const adminInfo = await apiRequest('/auth/me');
            showAdminPanel(adminInfo);
          } catch (error) {
            showError('Ошибка входа после регистрации');
          }
        }, 1000);
      } catch (error) {
        showError(error.message || 'Ошибка регистрации');
      }
    });
  }

  function showError(message) {
    if (errorMessage) {
      errorMessage.textContent = message;
      errorMessage.style.display = 'block';
      successMessage.style.display = 'none';
    }
  }

  function showSuccess(message) {
    if (successMessage) {
      successMessage.textContent = message;
      successMessage.style.display = 'block';
      errorMessage.style.display = 'none';
    }
  }

  function hideMessages() {
    if (errorMessage) errorMessage.style.display = 'none';
    if (successMessage) successMessage.style.display = 'none';
  }

  function showAdminPanel(adminInfo) {
    if (loginSection) loginSection.style.display = 'none';
    if (adminPanel) {
      adminPanel.style.display = 'block';
      const adminInfoElement = document.getElementById('admin-info');
      if (adminInfoElement) {
        adminInfoElement.textContent = `Вы вошли как: ${adminInfo.login} (${adminInfo.email})`;
      }
      // Инициализация и загрузка только для текущей страницы
      if (document.getElementById('leads-card')) {
        initLeadsHandlers();
        setTimeout(loadScoredLeads, 100);
      }
      if (document.getElementById('add-service-btn')) {
        initServicesHandlers();
        setTimeout(loadServices, 100);
      }
    }
  }
}

// Управление услугами
let currentEditingServiceId = null;

const SERVICES_PAGE_SIZE = 10;
let _allServices = [];
let _servicesCurrentPage = 1;

async function loadServices() {
  const tbody = document.getElementById('services-table-body');
  if (!tbody) return;

  try {
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Загрузка...</td></tr>';
    const services = await apiRequest('/admin/services/?limit=500');
    _allServices = services;
    _servicesCurrentPage = 1;

    if (!services.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty">Нет услуг. Добавьте первую услугу.</td></tr>';
      document.getElementById('services-pagination').style.display = 'none';
      return;
    }

    renderServicesPage(1);
    updateServicesPagination();
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="5" class="error">Ошибка загрузки: ${error.message}</td></tr>`;
    document.getElementById('services-pagination').style.display = 'none';
  }
}

function renderServicesPage(page) {
  const tbody = document.getElementById('services-table-body');
  if (!tbody) return;
  const start = (page - 1) * SERVICES_PAGE_SIZE;
  const slice = _allServices.slice(start, start + SERVICES_PAGE_SIZE);
  tbody.innerHTML = slice.map(service => `
    <tr>
      <td>${service.id}</td>
      <td>${escapeHtml(service.name)}</td>
      <td>${escapeHtml(service.description || '—')}</td>
      <td>${formatDate(service.created_at)}</td>
      <td class="actions">
        <button onclick="editService(${service.id})" class="btn btn--small btn--secondary">Редактировать</button>
        <button onclick="deleteService(${service.id})" class="btn btn--small btn--danger">Удалить</button>
      </td>
    </tr>
  `).join('');
}

function updateServicesPagination() {
  const wrap = document.getElementById('services-pagination');
  if (!wrap) return;
  const totalPages = Math.ceil(_allServices.length / SERVICES_PAGE_SIZE) || 1;
  if (totalPages <= 1) {
    wrap.style.display = 'none';
    return;
  }
  wrap.style.display = 'flex';
  wrap.innerHTML = `
    <span class="pagination__info">Стр. ${_servicesCurrentPage} из ${totalPages}</span>
    <div class="pagination__arrows">
      <button type="button" class="pagination__arrow" id="services-prev" ${_servicesCurrentPage <= 1 ? 'disabled' : ''} title="Предыдущая">‹</button>
      <button type="button" class="pagination__arrow" id="services-next" ${_servicesCurrentPage >= totalPages ? 'disabled' : ''} title="Следующая">›</button>
    </div>
  `;
  const prev = document.getElementById('services-prev');
  const next = document.getElementById('services-next');
  if (prev && !prev.disabled) prev.addEventListener('click', () => { _servicesCurrentPage--; renderServicesPage(_servicesCurrentPage); updateServicesPagination(); scrollToTop(); });
  if (next && !next.disabled) next.addEventListener('click', () => { _servicesCurrentPage++; renderServicesPage(_servicesCurrentPage); updateServicesPagination(); scrollToTop(); });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatDate(dateString) {
  if (!dateString) return '—';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function openServiceModal(serviceId = null) {
  currentEditingServiceId = serviceId;
  const modal = document.getElementById('service-modal');
  const form = document.getElementById('service-form');
  const title = document.getElementById('modal-title');
  const nameInput = document.getElementById('service-name');
  const descriptionInput = document.getElementById('service-description');

  if (serviceId) {
    title.textContent = 'Редактировать услугу';
    // Загружаем данные услуги
    apiRequest(`/admin/services/${serviceId}`).then(service => {
      nameInput.value = service.name;
      descriptionInput.value = service.description || '';
    }).catch(error => {
      showServiceError('Ошибка загрузки услуги: ' + error.message);
    });
  } else {
    title.textContent = 'Добавить услугу';
    form.reset();
  }

  modal.style.display = 'flex';
}

function closeServiceModal() {
  const modal = document.getElementById('service-modal');
  modal.style.display = 'none';
  currentEditingServiceId = null;
  document.getElementById('service-form').reset();
}

async function saveService(event) {
  event.preventDefault();
  hideServiceMessages();

  const nameInput = document.getElementById('service-name');
  const descriptionInput = document.getElementById('service-description');
  const name = nameInput.value.trim();
  const description = descriptionInput.value.trim();

  if (!name) {
    showServiceError('Название услуги обязательно');
    return;
  }

  try {
    const data = { name, description: description || null };
    
    if (currentEditingServiceId) {
      await apiRequest(`/admin/services/${currentEditingServiceId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
      showServiceSuccess('Услуга успешно обновлена');
    } else {
      await apiRequest('/admin/services/', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      showServiceSuccess('Услуга успешно добавлена');
    }

    closeServiceModal();
    loadServices();
  } catch (error) {
    showServiceError(error.message || 'Ошибка сохранения услуги');
  }
}

async function deleteService(serviceId) {
  if (!confirm('Вы уверены, что хотите удалить эту услугу?')) {
    return;
  }

  try {
    await apiRequest(`/admin/services/${serviceId}`, {
      method: 'DELETE',
    });
    showServiceSuccess('Услуга успешно удалена');
    loadServices();
  } catch (error) {
    showServiceError(error.message || 'Ошибка удаления услуги');
  }
}

function editService(serviceId) {
  openServiceModal(serviceId);
}

function showServiceError(message) {
  const errorEl = document.getElementById('error-message-services');
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.style.display = 'block';
    document.getElementById('success-message-services').style.display = 'none';
  }
}

function showServiceSuccess(message) {
  const successEl = document.getElementById('success-message-services');
  if (successEl) {
    successEl.textContent = message;
    successEl.style.display = 'block';
    document.getElementById('error-message-services').style.display = 'none';
  }
}

function hideServiceMessages() {
  const errorEl = document.getElementById('error-message-services');
  const successEl = document.getElementById('success-message-services');
  if (errorEl) errorEl.style.display = 'none';
  if (successEl) successEl.style.display = 'none';
}

// Инициализация обработчиков для управления услугами
let servicesHandlersInitialized = false;
function initServicesHandlers() {
  if (servicesHandlersInitialized) return;
  servicesHandlersInitialized = true;

  const addServiceBtn = document.getElementById('add-service-btn');
  const serviceForm = document.getElementById('service-form');

  if (addServiceBtn) {
    addServiceBtn.addEventListener('click', () => openServiceModal());
  }

  if (serviceForm) {
    serviceForm.addEventListener('submit', saveService);
  }

  // Закрытие модального окна при клике вне его
  const modal = document.getElementById('service-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeServiceModal();
      }
    });
  }
}

// Инициализация при загрузке страницы (обработчики лидов/услуг подключаются в showAdminPanel по наличию элементов)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Экспорт функций для использования в HTML
window.editService = editService;
window.deleteService = deleteService;
window.closeServiceModal = closeServiceModal;
window.openLeadModal = openLeadModal;
window.closeLeadModal = closeLeadModal;

// Выход
function logout() {
  tokenStorage.remove();
  window.location.reload();
}


// ==========================================
// Аналитика заявок (скоринг лидов)
// ==========================================
const LEADS_PAGE_SIZE = 10;
let _allLeads = [];
let _leadsCurrentPage = 1;

async function loadScoredLeads() {
  const tbody = document.getElementById('leads-table-body');
  if (!tbody) return;

  try {
    tbody.innerHTML = '<tr><td colspan="8" class="loading">Загрузка...</td></tr>';
    const leads = await apiRequest('/leads/scored/?limit=500');
    _allLeads = leads;
    _leadsCurrentPage = 1;

    // Статистика по всем заявкам
    let hot = 0, warm = 0, cold = 0;
    leads.forEach(l => {
      const t = l.scoring.temperature;
      if (t === 'горячий') hot++;
      else if (t === 'тёплый') warm++;
      else cold++;
    });
    setText('ls-total', leads.length);
    setText('ls-hot', hot);
    setText('ls-warm', warm);
    setText('ls-cold', cold);

    if (!leads.length) {
      tbody.innerHTML = '<tr><td colspan="8" class="empty">Нет заявок.</td></tr>';
      document.getElementById('leads-pagination').style.display = 'none';
      return;
    }

    renderLeadsPage(1);
    updateLeadsPagination();
  } catch (error) {
    tbody.innerHTML = `<tr><td colspan="8" class="error">Ошибка: ${error.message}</td></tr>`;
    document.getElementById('leads-pagination').style.display = 'none';
  }
}

function renderLeadsPage(page) {
  const tbody = document.getElementById('leads-table-body');
  if (!tbody) return;
  const start = (page - 1) * LEADS_PAGE_SIZE;
  const slice = _allLeads.slice(start, start + LEADS_PAGE_SIZE);
  tbody.innerHTML = slice.map(l => {
    const s = l.scoring;
    const cls = s.temperature === 'горячий' ? 'hot' : s.temperature === 'тёплый' ? 'warm' : 'cold';
    return `
      <tr onclick="openLeadModal(${l.id})" data-lead='${JSON.stringify(l).replace(/'/g, "&#39;")}'>
        <td><span class="badge badge--${cls}">${s.score}</span></td>
        <td>${escapeHtml(l.surname)} ${escapeHtml(l.name)}</td>
        <td>${escapeHtml(l.service || '—')}</td>
        <td>${escapeHtml(l.budget || '—')}</td>
        <td>${escapeHtml(l.deadline || '—')}</td>
        <td>${escapeHtml(s.department)}</td>
        <td><span class="badge badge--${s.needs_personal_manager ? 'yes' : 'no'}">${s.needs_personal_manager ? 'Да' : 'Нет'}</span></td>
        <td>${escapeHtml(s.priority)}</td>
      </tr>`;
  }).join('');
}

function updateLeadsPagination() {
  const wrap = document.getElementById('leads-pagination');
  if (!wrap) return;
  const totalPages = Math.ceil(_allLeads.length / LEADS_PAGE_SIZE) || 1;
  if (totalPages <= 1) {
    wrap.style.display = 'none';
    return;
  }
  wrap.style.display = 'flex';
  wrap.innerHTML = `
    <span class="pagination__info">Стр. ${_leadsCurrentPage} из ${totalPages}</span>
    <div class="pagination__arrows">
      <button type="button" class="pagination__arrow" id="leads-prev" ${_leadsCurrentPage <= 1 ? 'disabled' : ''} title="Предыдущая">‹</button>
      <button type="button" class="pagination__arrow" id="leads-next" ${_leadsCurrentPage >= totalPages ? 'disabled' : ''} title="Следующая">›</button>
    </div>
  `;
  const prev = document.getElementById('leads-prev');
  const next = document.getElementById('leads-next');
  if (prev && !prev.disabled) prev.addEventListener('click', () => { _leadsCurrentPage--; renderLeadsPage(_leadsCurrentPage); updateLeadsPagination(); scrollToTop(); });
  if (next && !next.disabled) next.addEventListener('click', () => { _leadsCurrentPage++; renderLeadsPage(_leadsCurrentPage); updateLeadsPagination(); scrollToTop(); });
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

// Открытие деталей заявки
let _scoredLeadsCache = [];
function openLeadModal(leadId) {
  const row = document.querySelector(`tr[onclick*="openLeadModal(${leadId})"]`);
  if (!row) return;
  let lead;
  try { lead = JSON.parse(row.dataset.lead); } catch { return; }

  const s = lead.scoring;
  const cls = s.temperature === 'горячий' ? 'hot' : s.temperature === 'тёплый' ? 'warm' : 'cold';

  const body = document.getElementById('lead-modal-body');
  const title = document.getElementById('lead-modal-title');
  title.textContent = `${lead.surname} ${lead.name} ${lead.patronymic || ''}`.trim();

  const scoreColor = cls === 'hot' ? '#ef4444' : cls === 'warm' ? '#f59e0b' : '#3b82f6';

  body.innerHTML = `
    <div class="lead-scoring-bar">
      <div class="lead-scoring-bar__score" style="color:${scoreColor}">${s.score}</div>
      <div class="lead-scoring-bar__meta">
        <p><strong>Температура:</strong> <span class="badge badge--${cls}">${s.temperature}</span>  &nbsp; <strong>Приоритет:</strong> ${s.priority}</p>
        <p><strong>Персональный менеджер:</strong> ${s.needs_personal_manager ? 'Рекомендуется' : 'Не требуется'}  &nbsp; <strong>Отдел:</strong> ${s.department}</p>
        <p style="color:var(--color-text-muted);font-size:0.85rem;margin-top:6px">${escapeHtml(s.summary)}</p>
      </div>
    </div>
    <div class="lead-detail">
      ${detailItem('Услуга', lead.service)}
      ${detailItem('Бюджет', lead.budget)}
      ${detailItem('Срок', lead.deadline)}
      ${detailItem('Ниша', lead.niche)}
      ${detailItem('Размер компании', lead.company_size)}
      ${detailItem('Размер бизнеса', lead.business_size)}
      ${detailItem('Роль', lead.role)}
      ${detailItem('Объём задач', lead.task_volume)}
      ${detailItem('Объём потребности', lead.need_volume)}
      ${detailItem('Тип задачи', lead.task_type)}
      ${detailItem('Интерес к продукту', lead.product_interest)}
      ${detailItem('Способ связи', lead.contact_method)}
      ${detailItem('Предпочтительная связь', lead.preferred_contact_method)}
      ${detailItem('Удобное время', lead.convenient_time)}
      ${detailItem('О бизнесе', lead.business_info, true)}
      ${detailItem('Комментарий', lead.comments, true)}
      ${detailItem('Дата заявки', lead.created_at ? formatDate(lead.created_at) : '—')}
    </div>
  `;

  document.getElementById('lead-detail-modal').style.display = 'flex';
}

function detailItem(label, value, full) {
  return `<div class="lead-detail__item${full ? ' lead-detail__item--full' : ''}">
    <span class="lead-detail__label">${escapeHtml(label)}</span>
    <span class="lead-detail__value">${escapeHtml(value || '—')}</span>
  </div>`;
}

function closeLeadModal() {
  document.getElementById('lead-detail-modal').style.display = 'none';
}

// Инициализация обработчиков для лидов
let leadsHandlersInitialized = false;
function initLeadsHandlers() {
  if (leadsHandlersInitialized) return;
  leadsHandlersInitialized = true;

  const refreshBtn = document.getElementById('refresh-leads-btn');
  if (refreshBtn) refreshBtn.addEventListener('click', loadScoredLeads);

  const modal = document.getElementById('lead-detail-modal');
  if (modal) modal.addEventListener('click', (e) => { if (e.target === modal) closeLeadModal(); });
}

// Экспорт для использования в других скриптах
window.adminAuth = {
  logout,
  apiRequest,
  isAuthenticated,
  loadServices,
  loadScoredLeads,
};
