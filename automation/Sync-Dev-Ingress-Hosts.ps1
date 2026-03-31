param(
    [string]$EntriesPath = "platform-stack/dev-ingress/hosts.example",
    [string]$HostsFilePath = "C:\Windows\System32\drivers\etc\hosts",
    [string]$BackupDir = "output/hosts-backups",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$args = @(
  "automation/sync_dev_ingress_hosts.py",
  "--entries-path", $EntriesPath,
  "--output-path", $HostsFilePath,
  "--backup-dir", $BackupDir
)

if ($Apply) {
  $args += "--write"
}

python @args
