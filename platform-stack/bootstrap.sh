#!/usr/bin/env sh
set -eu

stack_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_path="$stack_root/.env"
template_path="$stack_root/.env.example"
if [ "$#" -gt 0 ]; then
  workspace_root=$(CDPATH= cd -- "$1" && pwd)
else
  workspace_root=$(CDPATH= cd -- "$stack_root/../.." && pwd)
fi

if [ ! -f "$env_path" ]; then
  cp "$template_path" "$env_path"
fi

set_if_empty() {
  key=$1
  value=$2
  current=$(sed -n "s/^${key}=//p" "$env_path" | tail -n 1)
  if [ -n "$current" ]; then
    return
  fi
  temporary="$env_path.$$.tmp"
  awk -v key="$key" -v value="$value" '
    BEGIN { found = 0 }
    index($0, key "=") == 1 {
      print key "=" value
      found = 1
      next
    }
    { print }
    END { if (!found) print key "=" value }
  ' "$env_path" > "$temporary"
  mv "$temporary" "$env_path"
  printf 'Generated %s\n' "$key"
}

new_secret() {
  openssl rand -hex 32
}

set_if_empty LOTUS_WORKSPACE_ROOT "$workspace_root"
set_if_empty LOTUS_MANAGE_REPO_PATH "$workspace_root/lotus-manage"
set_if_empty LOTUS_CORE_REPO_PATH "$workspace_root/lotus-core"
set_if_empty LOTUS_PERFORMANCE_REPO_PATH "$workspace_root/lotus-performance"
set_if_empty LOTUS_REPORT_REPO_PATH "$workspace_root/lotus-report"
set_if_empty LOTUS_IDEA_REPO_PATH "$workspace_root/lotus-idea"
set_if_empty LOTUS_GATEWAY_REPO_PATH "$workspace_root/lotus-gateway"
set_if_empty LOTUS_WORKBENCH_REPO_PATH "$workspace_root/lotus-workbench"
set_if_empty LOTUS_CORE_POSTGRES_PASSWORD "$(new_secret)"
set_if_empty LOTUS_MANAGE_POSTGRES_PASSWORD "$(new_secret)"
set_if_empty LOTUS_REPORT_POSTGRES_PASSWORD "$(new_secret)"
set_if_empty GRAFANA_ADMIN_PASSWORD "$(new_secret)"
chmod 600 "$env_path"

printf 'Platform stack environment is ready at %s\n' "$env_path"
