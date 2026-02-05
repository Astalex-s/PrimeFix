#!/usr/bin/env bash
#
# Скрипт обновления Docker до версии с поддержкой API 1.44+ (требуется для docker compose up).
# Запускать с правами root или через sudo: sudo bash scripts/upgrade-docker.sh
#
set -euo pipefail

# Проверка root
if [[ ${EUID} -ne 0 ]]; then
  echo "Запустите скрипт с правами root: sudo bash $0" >&2
  exit 1
fi

echo "Добавление официального репозитория Docker..."
apt-get update -qq
apt-get install -y ca-certificates curl

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${VERSION_CODENAME:-$UBUNTU_CODENAME}") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Установка/обновление Docker Engine и Docker Compose plugin..."
apt-get update -qq
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Проверка версий..."
docker version
docker compose version

echo "Готово. Перезапустите стек: cd PrimeFix && docker compose up -d"
