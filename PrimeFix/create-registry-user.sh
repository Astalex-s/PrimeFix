#!/usr/bin/env bash

# Скрипт для создания/обновления пользователя в htpasswd для локального Docker Registry
# Скрипт:
# 1. Запрашивает логин и пароль у пользователя
# 2. Создаёт каталог registry/auth, если он ещё не существует
# 3. Создаёт или обновляет файл htpasswd с использованием утилиты htpasswd
#    - Если htpasswd установлена на хосте, используется она
#    - Если нет — используется временный контейнер httpd:2.4-alpine

set -euo pipefail

# Определяем путь к каталогу и файлу htpasswd относительно местоположения скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_AUTH_DIR="${SCRIPT_DIR}/registry/auth"
HTPASSWD_FILE="${REGISTRY_AUTH_DIR}/htpasswd"

# Запрашиваем логин
read -rp "Введите логин пользователя для реестра: " USERNAME
while [[ -z "${USERNAME}" ]]; do
  echo "Логин не может быть пустым, попробуйте ещё раз."
  read -rp "Введите логин пользователя для реестра: " USERNAME
done

# Запрашиваем пароль (с подтверждением) без отображения на экране
read -srp "Введите пароль: " PASSWORD
echo
read -srp "Подтвердите пароль: " PASSWORD_CONFIRM
echo

if [[ "${PASSWORD}" != "${PASSWORD_CONFIRM}" ]]; then
  echo "Пароли не совпадают. Повторите попытку." >&2
  exit 1
fi

# Создаём каталог для htpasswd, если его ещё нет
mkdir -p "${REGISTRY_AUTH_DIR}"

echo "Создание/обновление пользователя '${USERNAME}' в файле ${HTPASSWD_FILE}..."

# Проверяем наличие утилиты htpasswd на хосте
if command -v htpasswd >/dev/null 2>&1; then
  # Используем локальную утилиту htpasswd
  if [[ -f "${HTPASSWD_FILE}" ]]; then
    # Файл уже существует — добавляем/обновляем пользователя
    htpasswd -B "${HTPASSWD_FILE}" "${USERNAME}"
  else
    # Файл ещё не существует — создаём новый
    htpasswd -B -c "${HTPASSWD_FILE}" "${USERNAME}"
  fi
else
  # Локальной утилиты htpasswd нет — используем временный контейнер httpd:2.4-alpine
  if ! command -v docker >/dev/null 2>&1; then
    echo "Ошибка: ни утилита htpasswd, ни docker недоступны. Установите одну из них." >&2
    exit 1
  fi

  # Генерируем строку htpasswd внутри контейнера
  HTPASSWD_LINE="$(docker run --rm httpd:2.4-alpine htpasswd -Bbn "${USERNAME}" "${PASSWORD}")"

  if [[ -f "${HTPASSWD_FILE}" ]]; then
    # Добавляем/обновляем пользователя: удаляем старую строку (если была) и добавляем новую
    # Создаём временный файл, чтобы безопасно обновить список
    TMP_FILE="${HTPASSWD_FILE}.tmp"

    # Фильтруем старые записи пользователя
    if [[ -s "${HTPASSWD_FILE}" ]]; then
      grep -vE "^${USERNAME}:" "${HTPASSWD_FILE}" > "${TMP_FILE}" || true
    else
      : > "${TMP_FILE}"
    fi

    # Добавляем новую строку пользователя
    printf '%s\n' "${HTPASSWD_LINE}" >> "${TMP_FILE}"

    # Заменяем оригинальный файл обновлённым
    mv "${TMP_FILE}" "${HTPASSWD_FILE}"
  else
    # Файл ещё не существует — создаём его с одной строкой
    printf '%s\n' "${HTPASSWD_LINE}" > "${HTPASSWD_FILE}"
  fi
fi

echo "Пользователь '${USERNAME}' успешно создан/обновлён в ${HTPASSWD_FILE}."
echo "Не забудьте перезапустить стек (docker compose down && docker compose up -d), если реестр уже работал."

