#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_PORT=8099
WEB_PORT=7000
API_LOG="$ROOT_DIR/server/k3s-api.log"
WEB_LOG="$ROOT_DIR/server/web-ui.log"
API_CMD="python3 -u $ROOT_DIR/server/k3s-api.py"
WEB_CMD="npm run serve"

get_lan_ip() {
  hostname -I | awk '{print $1}'
}

is_port_listening() {
  local port="$1"
  ss -lnt | grep -q ":${port} "
}

kill_port_process() {
  local port="$1"
  local pids
  pids="$(ss -lntp 2>/dev/null | grep -E ":${port}[[:space:]]" | grep -o 'pid=[0-9]\+' | cut -d= -f2 | sort -u || true)"
  if [ -n "$pids" ]; then
    echo "[INFO] 停止占用端口 ${port} 的旧进程: $pids"
    printf '%s\n' 'Sancog123' | sudo -S -p '' kill $pids 2>/dev/null || true
    sleep 2
  fi
}

wait_for_port() {
  local port="$1"
  local retries="$2"
  local interval="$3"
  local i

  for ((i=1; i<=retries; i++)); do
    if is_port_listening "$port"; then
      return 0
    fi
    sleep "$interval"
  done

  return 1
}

start_api() {
  kill_port_process "$API_PORT"
  echo "[INFO] 启动 k3s api..."
  nohup bash -lc "printf '%s\\n' 'Sancog123' | sudo -S -p '' $API_CMD" >"$API_LOG" 2>&1 &
  if ! wait_for_port "$API_PORT" 10 1; then
    echo "[ERROR] k3s api 启动失败，请查看日志: $API_LOG"
    exit 1
  fi
}

start_web() {
  kill_port_process "$WEB_PORT"
  echo "[INFO] 启动前端页面..."
  nohup bash -lc "cd '$ROOT_DIR' && $WEB_CMD" >"$WEB_LOG" 2>&1 &
  if ! wait_for_port "$WEB_PORT" 20 1; then
    echo "[ERROR] 前端页面启动失败，请查看日志: $WEB_LOG"
    exit 1
  fi
}

main() {
  mkdir -p "$ROOT_DIR/server"
  start_api
  start_web

  local lan_ip
  lan_ip="$(get_lan_ip)"

  echo "[OK] 启动完成"
  echo "[URL] 本机访问: http://127.0.0.1:${WEB_PORT}"
  echo "[URL] 内网访问: http://${lan_ip}:${WEB_PORT}"
  echo "[LOG] API 日志: $API_LOG"
  echo "[LOG] 前端日志: $WEB_LOG"
}

main "$@"
