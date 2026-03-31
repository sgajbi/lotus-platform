param(
    [string]$EntriesPath = "platform-stack/dev-ingress/hosts.example",
    [string]$HostsFilePath = "C:\Windows\System32\drivers\etc\hosts",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"

$args = @(
  "automation/sync_dev_ingress_hosts.py",
  "--entries-path", $EntriesPath,
  "--output-path", $HostsFilePath
)

if ($Apply) {
  $args += "--write"
}

python @args
