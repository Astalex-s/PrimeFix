#!/usr/bin/env bash

# Скрипт для создания/обновления пользователя в htpasswd для локального Docker Registry
# Запускать из корня репозитория: bash scripts/create-registry-user.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REGISTRY_AUTH_DIR="${PROJECT_ROOT}/registry/auth"
HTPASSWD_FILE="${REGISTRY_AUTH_DIR}/htpasswd"

read -rp "Введите логин пользователя для реестра: " USERNAME
while [[ -z "${USERNAME}" ]]; do
  echo "Логин не может быть пустым, попробуйте ещё раз."
  read -rp "Введите логин пользователя для реестра: " USERNAME
done

read -srp "Введите пароль: " PASSWORD
echo
read -srp "Подтвердите пароль: " PASSWORD_CONFIRM
echo

if [[ "${PASSWORD}" != "${PASSWORD_CONFIRM}" ]]; then
  echo "Пароли не совпадают. Повторите попытку." >&2
  exit 1
fi

mkdir -p "${REGISTRY_AUTH_DIR}"
echo "Создание/обновление пользователя '${USERNAME}' в файле ${HTPASSWD_FILE}..."

if command -v htpasswd >/dev/null 2>&1; then
  if [[ -f "${HTPASSWD_FILE}" ]]; then
    htpasswd -B "${HTPASSWD_FILE}" "${USERNAME}"
  else
    htpasswd -B -c "${HTPASSWD_FILE}" "${USERNAME}"
  fi
else
  if ! command -v docker >/dev/null 2>&1; then
    echo "Ошибка: ни утилита htpasswd, ни docker недоступны. Установите одну из них." >&2
    exit 1
  fi

  HTPASSWD_LINE="$(docker run --rm httpd:2.4-alpine htpasswd -Bbn "${USERNAME}" "${PASSWORD}")"

  if [[ -f "${HTPASSWD_FILE}" ]]; then
    TMP_FILE="${HTPASSWD_FILE}.tmp"
    if [[ -s "${HTPASSWD_FILE}" ]]; then
      grep -vE "^${USERNAME}:" "${HTPASSWD_FILE}" > "${TMP_FILE}" || true
    else
      : > "${TMP_FILE}"
    fi
    printf '%s\n' "${HTPASSWD_LINE}" >> "${TMP_FILE}"
    mv "${TMP_FILE}" "${HTPASSWD_FILE}"
  else
    printf '%s\n' "${HTPASSWD_LINE}" > "${HTPASSWD_FILE}"
  fi
fi

echo "Пользователь '${USERNAME}' успешно создан/обновлён в ${HTPASSWD_FILE}."
echo "Не забудьте перезапустить стек (docker compose down && docker compose up -d), если реестр уже работал."
