#!/usr/bin/env sh
set -eu
umask 077

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

read_current_value() {
  key=$1
  current=$(sed -n "s/^${key}=//p" "$env_path" | tail -n 1)
  terminal_carriage_return=$(printf '\r')
  case "$current" in
    *"$terminal_carriage_return") current=${current%"$terminal_carriage_return"} ;;
  esac
  printf '%s' "$current"
}

set_if_empty() {
  key=$1
  value=$2
  current=$(read_current_value "$key")
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

reject_legacy_secret_default() {
  key=$1
  legacy_value=$2
  current=$(read_current_value "$key")
  if [ "$current" = "$legacy_value" ]; then
    printf 'Refusing the legacy tracked default for %s. Clear it only when initializing a fresh database, or replace it with an operator-managed secret after following the documented database migration path.\n' "$key" >&2
    return 1
  fi
}

reject_unsafe_database_uri_component() {
  key=$1
  current=$(read_current_value "$key")
  case "$current" in
    "") ;;
    *[!A-Za-z0-9._~-]*)
      printf '%s contains characters that are unsafe in the platform stack PostgreSQL URI. Use only letters, numbers, dot, underscore, tilde, and hyphen.\n' "$key" >&2
      return 1
      ;;
  esac
}

set_secret_if_empty() {
  key=$1
  current=$(read_current_value "$key")
  if [ -n "$current" ]; then
    return
  fi
  if ! value=$(new_secret); then
    printf 'Failed to generate %s\n' "$key" >&2
    return 1
  fi
  if [ -z "$value" ]; then
    printf 'Refusing to write an empty generated secret for %s\n' "$key" >&2
    return 1
  fi
  set_if_empty "$key" "$value"
}

reject_legacy_secret_default LOTUS_CORE_POSTGRES_PASSWORD password
for database_uri_component in \
  LOTUS_CORE_POSTGRES_USER LOTUS_CORE_POSTGRES_PASSWORD LOTUS_CORE_POSTGRES_DB \
  LOTUS_MANAGE_POSTGRES_USER LOTUS_MANAGE_POSTGRES_PASSWORD LOTUS_MANAGE_POSTGRES_DB \
  LOTUS_REPORT_POSTGRES_USER LOTUS_REPORT_POSTGRES_PASSWORD LOTUS_REPORT_POSTGRES_DB
do
  reject_unsafe_database_uri_component "$database_uri_component"
done
set_if_empty LOTUS_WORKSPACE_ROOT "$workspace_root"
set_if_empty LOTUS_MANAGE_REPO_PATH "$workspace_root/lotus-manage"
set_if_empty LOTUS_CORE_REPO_PATH "$workspace_root/lotus-core"
set_if_empty LOTUS_PERFORMANCE_REPO_PATH "$workspace_root/lotus-performance"
set_if_empty LOTUS_REPORT_REPO_PATH "$workspace_root/lotus-report"
set_if_empty LOTUS_IDEA_REPO_PATH "$workspace_root/lotus-idea"
set_if_empty LOTUS_GATEWAY_REPO_PATH "$workspace_root/lotus-gateway"
set_if_empty LOTUS_WORKBENCH_REPO_PATH "$workspace_root/lotus-workbench"
set_secret_if_empty LOTUS_CORE_POSTGRES_PASSWORD
set_secret_if_empty LOTUS_MANAGE_POSTGRES_PASSWORD
set_secret_if_empty LOTUS_REPORT_POSTGRES_PASSWORD
set_secret_if_empty GRAFANA_ADMIN_PASSWORD
chmod 600 "$env_path"

printf 'Platform stack environment is ready at %s\n' "$env_path"
