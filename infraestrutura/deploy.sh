#!/usr/bin/env bash
# Transfere o simulador para a VM via SCP e executa.
# Uso: ./deploy.sh <IP_DA_VM> [usuario] [chave_privada]
set -euo pipefail

IP="${1:?Informe o IP da VM}"
USUARIO="${2:-devops}"
CHAVE="${3:-$HOME/.ssh/id_ed25519}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SSH_OPTS=(-i "$CHAVE" -o StrictHostKeyChecking=accept-new)

scp "${SSH_OPTS[@]}" -r "$RAIZ/simulador/." "$USUARIO@$IP:/opt/supermercado/simulador/"

ssh "${SSH_OPTS[@]}" "$USUARIO@$IP" \
  "cd /opt/supermercado/simulador && python3 simulador.py && ls -l /opt/supermercado/dados && tail -n 5 /opt/supermercado/dados/estoque.csv"
