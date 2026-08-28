#!/usr/bin/env bash
# Idempotent system-package bootstrap for the WSL2 Ubuntu that hosts both tool
# environments (PLAN Phase 1). Run as root: sudo bash envs/apt_base.sh
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq \
  build-essential cmake curl ca-certificates git unzip \
  libcurl4-openssl-dev libssl-dev libxml2-dev \
  libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
  libfreetype6-dev libpng-dev libtiff-dev libjpeg-dev \
  libuv1-dev libnlopt-dev

echo "apt base done"
