#requires -Version 7.5
param(
    [Parameter(Mandatory)][ValidateSet('DryRun','ArchiveVerify','Retire')][string]$Stage,
    [Parameter(Mandatory)][string]$ProjectsRoot,
    [Parameter(Mandatory)][string]$WorkbenchRepoPath,
    [Parameter(Mandatory)][string]$RuntimeHolder,
    [Parameter(Mandatory)][string]$Disposition,
    [Parameter(Mandatory)][string]$ExpectedDispositionSha256,
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Inventory,
    [string]$VerificationReceipt,
    [string]$ArchiveDisposition,
    [string]$ExpectedVerificationReceiptSha256
)
$ErrorActionPreference = 'Stop'
$helperRoot = Split-Path -Parent $PSScriptRoot
$policyCli = Join-Path $PSScriptRoot 'resource_recovery/cli.py'
$script:operation = $null
$script:authority = $null
$script:nativeStatus = 0
$script:approval = $null
$script:receiptPath = $null
$script:journal = $null
$sourceHandles = @()
$script:liveAdmission = $null
$script:runId = $null
$exitStatus = 1

function Assert-HelperClosure {
    if (-not $script:approval) { throw 'REVIEWED_DISPOSITION_REQUIRED' }
    $expectedFiles = @('automation/Invoke-ResourceOnlyRecovery.ps1','automation/resource_recovery/__init__.py',
        'automation/resource_recovery/policy.py','automation/resource_recovery/archive_verification.py',
        'automation/resource_recovery/volume_io.py','automation/resource_recovery/cli.py','automation/canonical_docker_ownership.py')
    $actualFiles = @($script:approval.helper_files.PSObject.Properties.Name)
    if ($actualFiles.Count -ne $expectedFiles.Count -or @(Compare-Object $actualFiles $expectedFiles).Count) { throw 'HELPER_CLOSURE_REQUIRED' }
    if ([IO.Path]::GetFullPath($script:approval.helper_root) -ne [IO.Path]::GetFullPath($helperRoot)) { throw 'HELPER_ROOT_CHANGED' }
    if (Test-Path -LiteralPath (Join-Path $helperRoot 'automation/__init__.py')) { throw 'UNREVIEWED_PACKAGE_INITIALIZER' }
    foreach ($relative in $expectedFiles) {
        $candidate = Join-Path $helperRoot $relative
        $entry = Get-Item -LiteralPath $candidate
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'REPARSE_PATH_REFUSED' }
        $parent = $entry.Directory
        while ($parent) {
            if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'REPARSE_PATH_REFUSED' }
            $parent = $parent.Parent
        }
        $expectedHash = $script:approval.helper_files.$relative
        if ((Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expectedHash) { throw 'HELPER_SOURCE_CHANGED' }
    }
}

function Get-SafeRecoveryReason {
    param([string]$Message,[string]$Fallback)
    if ($Message -cnotmatch '^[A-Z][A-Z0-9_]{1,79}$') { return $Fallback }
    # Closed vocabulary from the reviewed source closure, never arbitrary child text.
    $paths = @($PSCommandPath,$policyCli,(Join-Path $PSScriptRoot 'resource_recovery/policy.py'),
        (Join-Path $PSScriptRoot 'resource_recovery/archive_verification.py'))
    foreach ($path in $paths) {
        $text = Get-Content -LiteralPath $path -Raw
        $codes = [regex]::Matches($text, '[\x22\x27]([A-Z][A-Z0-9]*_[A-Z0-9_]+)[\x22\x27]')
        foreach ($code in $codes) { if ($code.Groups[1].Value -ceq $Message) { return $Message } }
    }
    return $Fallback
}

function Invoke-Policy {
    param([string[]]$Arguments,[switch]$PassThru)
    Assert-HelperClosure
    if ($script:approval.schema_version -eq 'lotus.resource-recovery.retirement.v2') {
        $Arguments += @('--archive-approval',$ArchiveDisposition)
    }
    if('--plan' -notin $Arguments){$Arguments+=@('--plan',$Plan,'--inventory',$Inventory)}
    $lines = @(& python -I $policyCli @Arguments --approval $Disposition `
        --expected-approval-sha256 $ExpectedDispositionSha256 --root $helperRoot 2>$null)
    $script:nativeStatus = $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) {
        $reason = if ($lines.Count -eq 1) { Get-SafeRecoveryReason ([string]$lines[0]) 'RESOURCE_RECOVERY_POLICY_REFUSED' } else { 'RESOURCE_RECOVERY_POLICY_REFUSED' }
        throw $reason
    }
    if ($PassThru) { return $lines }
}

function Write-PrivateJson {
    param([string]$Path, $Value)
    $temporary = "$Path.$([guid]::NewGuid().ToString('N')).tmp"
    $bytes=[Text.UTF8Encoding]::new($false).GetBytes(($Value|ConvertTo-Json -Depth 100))
    $stream=[IO.File]::Open($temporary,'CreateNew','Write','None')
    try{$stream.Write($bytes,0,$bytes.Length);$stream.Flush($true)}finally{$stream.Dispose()}
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Save-Journal {
    if ($script:receiptPath) { Write-PrivateJson $script:receiptPath $script:journal }
}

function Assert-Admission {
    if (-not $script:operation) { throw 'LIVE_OPERATION_REQUIRED' }
    try { & $script:authority {
        param($root, $token, $stream, $holder, $workbench)
        Assert-CanonicalRuntimeOperationFence -ProjectsRoot $root -OperationToken $token -Fence $stream
        Invoke-CanonicalReservation -Action preflight-operation -ProjectsRoot $root -Holder $holder `
            -WorkbenchRepoPath $workbench -OperationToken $token | Out-Null
    } $ProjectsRoot $script:operation.Token $script:operation.Lock $RuntimeHolder $WorkbenchRepoPath
    } catch {
        if ($LASTEXITCODE -ne 0) { $script:nativeStatus = $LASTEXITCODE }
        throw
    }
    Invoke-Policy @('validate-local')
    $head = & git -C (Join-Path $ProjectsRoot 'lotus-platform') rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $head.Trim() -ne $script:approval.primary_head) { throw 'PRIMARY_SOURCE_CHANGED' }
    $dirty = & git -C (Join-Path $ProjectsRoot 'lotus-platform') status --porcelain --untracked-files=no
    if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'PRIMARY_SOURCE_DIRTY' }
}

function Invoke-RecoveryDocker {
    param([string]$Context, [string[]]$Arguments,[int]$LiveTargetIndex=-1)
    Assert-Admission
    $expectedDaemon = if ($Context -eq $script:approval.source_context) { $script:approval.source_daemon }
        elseif ($Context -eq $script:approval.verification_context) { $script:approval.verification_daemon }
        else { throw 'UNAPPROVED_CONTEXT' }
    $observedDaemon = & docker --context $Context info --format '{{.ID}}' 2>$null
    $script:nativeStatus = $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) { throw 'DAEMON_OBSERVATION_FAILED' }
    if (($observedDaemon -join '').Trim() -ne $expectedDaemon) { throw 'DAEMON_IDENTITY_CHANGED' }
    if($LiveTargetIndex -ge 0){Assert-LiveAction $LiveTargetIndex -AdmissionChecked}
    # A closed native argument list, not a caller script/callback or shell expression.
    $lines = & docker --context $Context @Arguments 2>$null
    $script:nativeStatus = $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) { throw 'DOCKER_COMMAND_FAILED' }
    return $lines
}

function Get-Snapshot {
    param([string]$Phase,[int]$TargetIndex = -1)
    $started=[DateTime]::UtcNow.ToString('o')
    Assert-Admission
    $status=& $script:authority {param($root,$holder,$workbench)
        Invoke-CanonicalReservation -Action status -ProjectsRoot $root -Holder $holder -WorkbenchRepoPath $workbench
    } $ProjectsRoot $RuntimeHolder $WorkbenchRepoPath
    $expected=$script:approval.runtime_authority
    if($status.current.holder -cne $expected.holder -or $status.scopeDigest -cne $expected.scope_digest -or
       $status.current.operation.token -cne $script:operation.Token -or
       @(Compare-Object @($status.scope.sources.PSObject.Properties.Name) @($expected.source_heads.PSObject.Properties.Name)).Count -or
       @($expected.source_heads.PSObject.Properties | Where-Object {$status.scope.sources.($_.Name) -cne $_.Value}).Count){
        throw 'LIVE_AUTHORITY_CHANGED'
    }
    $context = $script:approval.source_context
    $daemon = (Invoke-RecoveryDocker $context @('info','--format','{{.ID}}')) -join ''
    $ids = @(Invoke-RecoveryDocker $context @('container','ls','--all','--quiet','--no-trunc'))
    $containers = @()
    foreach ($id in $ids) {
        $containers += @(((Invoke-RecoveryDocker $context @('container','inspect',$id)) -join "`n") | ConvertFrom-Json -DateKind String)
    }
    $images = @(); $volumes = @()
    $targets = if ($TargetIndex -ge 0) { @($script:approval.targets[$TargetIndex]) } else { @($script:approval.targets) }
    foreach ($target in $targets) {
        $record = @(((Invoke-RecoveryDocker $context @($target.kind,'inspect',$target.id)) -join "`n") | ConvertFrom-Json -DateKind String)
        if ($record.Count -ne 1) { throw 'EXACT_INSPECT_REQUIRED' }
        if ($target.kind -eq 'image') { $images += $record[0] } else { $volumes += $record[0] }
    }
    $after=@(Invoke-RecoveryDocker $context @('container','ls','--all','--quiet','--no-trunc'))
    if(@(Compare-Object $ids $after).Count -or @($ids|Sort-Object -Unique).Count -ne $ids.Count){throw 'LIVE_CONSUMER_LIST_CHANGED'}
    $roots=& python -I $policyCli protected-roots --root $helperRoot --projects-root $ProjectsRoot --workbench-repo-path $WorkbenchRepoPath
    if($LASTEXITCODE -ne 0){throw 'CURRENT_PROTECTED_ROOTS_FAILED'}
    $result = @{schema_version='lotus.resource-recovery.live-observation.v1';run_id=$script:runId;operation_token=$script:operation.Token;
        phase=$Phase;target_indexes=@(if($TargetIndex -ge 0){$TargetIndex}else{0..($script:approval.targets.Count-1)});
        approval_sha256=$ExpectedDispositionSha256;discovery_receipt_sha256=$script:approval.discovery.capture_receipt_sha256;
        collection_started_at=$started;collection_finished_at=$null;source_context=$context;source_daemon=$daemon.Trim();
        holder=$RuntimeHolder;scope_digest=$status.scopeDigest;source_heads=$status.scope.sources;helper_files=$script:approval.helper_files;
        container_ids_before=$ids;container_ids_after=$after;containers=$containers;images=$images;volumes=$volumes;
        verification_context=$script:approval.verification_context;verification_daemon=$null;
        protected_checkout_paths=@(($roots -join "`n")|ConvertFrom-Json)}
    if (@($script:approval.targets | Where-Object kind -eq 'image').Count -gt 0) {
        if (-not $script:approval.verification_context) { throw 'DISTINCT_VERIFICATION_DAEMON_REQUIRED' }
        $verifyId = (Invoke-RecoveryDocker $script:approval.verification_context @('info','--format','{{.ID}}')) -join ''
        $result.verification_daemon = $verifyId.Trim()
        $result.verification_context = $script:approval.verification_context
    }
    $result.collection_finished_at=[DateTime]::UtcNow.ToString('o')
    return $result
}

function Prepare-Current {
    param([string]$Directory, [string]$Phase, [int]$TargetIndex = -1)
    $snapshotPath = Join-Path $runDirectory "snapshot-$([guid]::NewGuid().ToString('N')).json"
    $observation=Get-Snapshot -Phase $Phase -TargetIndex $TargetIndex
    Write-PrivateJson $snapshotPath $observation
    $script:sourceHandles+=[IO.File]::Open($snapshotPath,'Open','Read','Read')
    $sha=(Get-FileHash -LiteralPath $snapshotPath).Hash.ToLowerInvariant()
    $liveArgs=@('--snapshot',$snapshotPath,'--expected-snapshot-sha256',$sha)
    if ($TargetIndex -ge 0) {
        Invoke-Policy (@('check-target','--directory',$Directory,'--phase',$Phase,'--target-index',[string]$TargetIndex)+$liveArgs)
    } else {
        Invoke-Policy (@('prepare','--directory',$Directory,'--phase',$Phase)+$liveArgs)
    }
    $script:liveAdmission=$observation
    $script:journal.admissions+=@{path=$snapshotPath;sha256=$sha;approval_sha256=$ExpectedDispositionSha256;
        discovery_receipt_sha256=$script:approval.discovery.capture_receipt_sha256;target_indexes=$observation.target_indexes}
    Save-Journal
    if($TargetIndex -ge 0){return}
    return (Get-Content -LiteralPath (Join-Path $Directory 'prepared.json') -Raw | ConvertFrom-Json)
}

function Assert-LiveAction {
    param([int]$Index,[switch]$AdmissionChecked)
    if(-not $AdmissionChecked){Assert-Admission}
    if(-not $script:liveAdmission -or $Index -notin $script:liveAdmission.target_indexes){throw 'LIVE_TARGET_ADMISSION_REQUIRED'}
    $start=[DateTimeOffset]::Parse($script:liveAdmission.collection_started_at)
    $now=[DateTimeOffset]::UtcNow
    if($start -gt $now -or ($now-$start).TotalSeconds -gt 300){throw 'STALE_LIVE_ADMISSION'}
}

function Invoke-VolumeWorker {
    param([string]$Volume, [string]$Directory, [string]$Action,[int]$LiveTargetIndex=-1)
    $worker = Join-Path $PSScriptRoot 'resource_recovery/volume_io.py'
    $sourceMount = "type=volume,source=$Volume,target=/source"
    if ($Action -eq 'archive') { $sourceMount += ',readonly' }
    $workerName = "lotus-resource-worker-$([guid]::NewGuid().ToString('N'))"
    $script:journal.helper_resources += @{ kind='container'; id=$workerName; context=$script:approval.source_context; status='run_requested'; action=$Action }
    $workerRecord = $script:journal.helper_resources[-1]
    Save-Journal
    Invoke-RecoveryDocker $script:approval.source_context @(
        'run','--rm','--name',$workerName,'--label',"com.lotus.resource-recovery.operation=$($script:operation.Token)",
        '--network','none','--read-only','--cap-drop','ALL',
        '--cap-add','CHOWN','--cap-add','DAC_OVERRIDE','--cap-add','FOWNER','--cap-add','FSETID',
        '--memory','256m','--cpus','1','--pids-limit','64',
        '--mount',$sourceMount,'--mount',"type=bind,source=$Directory,target=/archive",
        '--mount',"type=bind,source=$worker,target=/worker.py,readonly",
        $script:approval.archiver_image,'python3','/worker.py',$Action,
        '--max-bytes',[string]$script:approval.max_archive_bytes
    ) -LiveTargetIndex $LiveTargetIndex | Out-Null
    $workerRecord.status = 'native_worker_completed_auto_remove_requested'
    Save-Journal
}

function Archive-Target {
    param($Item, [string]$Directory, [int]$Index)
    if ($Item.target.kind -eq 'image') {
        $context = $script:approval.source_context
        $tags = @($Item.original.RepoTags)
        $selectors = if ($tags.Count -gt 0) { $tags } else { @($Item.target.id) }
        foreach($tag in $tags){
            $mapped=@(Invoke-RecoveryDocker $context @('image','ls','--quiet','--no-trunc',$tag))
            if($mapped.Count -ne 1 -or $mapped[0] -cne $Item.target.id){throw 'ARCHIVE_TAG_ID_CHANGED'}
        }
        Assert-LiveAction $Index
        Invoke-RecoveryDocker $context (@('image','save','--output',(Join-Path $Directory 'image.tar')) + $selectors) -LiveTargetIndex $Index | Out-Null
        $proofLines = @(Invoke-Policy -Arguments @('verify-archive','--directory',$archiveDirectory,'--target-index',[string]$Index) -PassThru)
        if ($proofLines.Count -ne 2 -or $proofLines[1] -cne 'RESOURCE_RECOVERY_CHECK_PASSED') { throw 'IMAGE_IDENTITY_PROOF_REQUIRED' }
        $identity = $proofLines[0] | ConvertFrom-Json -DateKind String
        if ($identity.source_id -cne $Item.target.id -or $identity.restore_ids.Count -lt 1 -or $identity.restore_ids.Count -gt 2) { throw 'IMAGE_IDENTITY_PROOF_REQUIRED' }
        $verifyContext = $script:approval.verification_context
        $existing = @(Invoke-RecoveryDocker $verifyContext @('image','ls','--quiet','--no-trunc'))
        foreach ($id in $identity.restore_ids) {
            if ($existing -ccontains $id) { throw 'VERIFICATION_IMAGE_ALREADY_PRESENT' }
        }
        foreach ($tag in $tags) {
            $tagIds = @(Invoke-RecoveryDocker $verifyContext @('image','ls','--quiet','--no-trunc',$tag))
            if ($tagIds.Count -gt 0) { throw 'VERIFICATION_TAG_ALREADY_PRESENT' }
        }
        $script:journal.helper_resources += @{ kind='image'; id=$Item.target.id; restore_ids=@($identity.restore_ids); archive_sha256=$identity.archive_sha256; context=$verifyContext; tags=$tags; status='load_requested' }
        $imageRecord = $script:journal.helper_resources[-1]
        Save-Journal
        Invoke-RecoveryDocker $verifyContext @('image','load','--input',(Join-Path $Directory 'image.tar')) | Out-Null
        $loaded = @(Invoke-RecoveryDocker $verifyContext @('image','ls','--quiet','--no-trunc'))
        $matched = @($identity.restore_ids | Where-Object { $loaded -ccontains $_ })
        if ($matched.Count -ne 1) { throw 'EXACT_RESTORE_IDENTITY_REQUIRED' }
        $restored = @(((Invoke-RecoveryDocker $verifyContext @('image','inspect',$matched[0])) -join "`n") | ConvertFrom-Json -DateKind String)
        if ($restored.Count -ne 1) { throw 'EXACT_RESTORE_INSPECT_REQUIRED' }
        $imageRecord.restored_id = $restored[0].Id
        $imageRecord.status = 'restored_inspected_pending_verification'
        Save-Journal
        Write-PrivateJson (Join-Path $Directory 'restored.json') $restored[0]
        # Re-evaluate archive and restored metadata through the same policy boundary.
        Invoke-Policy @('verify-archive','--directory',$archiveDirectory,'--target-index',[string]$Index,'--check-restored') | Out-Null
        $imageRecord.status = 'restore_completed_retained'
        Save-Journal
    } else {
        Assert-LiveAction $Index
        Invoke-VolumeWorker $Item.target.id $Directory 'archive' $Index
        Invoke-Policy @('verify-archive','--directory',$archiveDirectory,'--target-index',[string]$Index)
        $restoreName = "lotus-resource-recovery-$([guid]::NewGuid().ToString('N'))"
        $script:journal.helper_resources += @{ kind='volume'; id=$restoreName; context=$script:approval.source_context; status='creation_requested' }
        $volumeRecord = $script:journal.helper_resources[-1]
        Save-Journal
        Invoke-RecoveryDocker $script:approval.source_context @('volume','create','--label',"com.lotus.resource-recovery.operation=$($script:operation.Token)",$restoreName) | Out-Null
        $volumeRecord.status = 'created'
        Save-Journal
        Invoke-VolumeWorker $restoreName $Directory 'restore'
        # Keep the verification resource for explicit operator disposition, even on success.
        $volumeRecord.status = 'restore_completed_retained'
        Save-Journal
    }
}

try {
    if ([string]::IsNullOrWhiteSpace($RuntimeHolder)) { throw 'EXPLICIT_HOLDER_REQUIRED' }
    if ((Get-FileHash -LiteralPath $Disposition -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedDispositionSha256) { throw 'DISPOSITION_DIGEST_CHANGED' }
    $script:approval = Get-Content -LiteralPath $Disposition -Raw | ConvertFrom-Json -DateKind String
    if ($script:approval.schema_version -eq 'lotus.resource-recovery.retirement.v2' -and
        ($Stage -ne 'Retire' -or -not $ArchiveDisposition)) { throw 'RETIREMENT_RENEWAL_SCOPE_REQUIRED' }
    Assert-HelperClosure
    foreach ($relative in $script:approval.helper_files.PSObject.Properties.Name) {
        $sourceHandles += [IO.File]::Open((Join-Path $helperRoot $relative),'Open','Read','Read')
    }
    $evidencePaths=@($Disposition,$Plan,$Inventory,$script:approval.discovery.capture_path,$script:approval.discovery.capture_receipt_path)
    foreach($call in $script:approval.discovery.native_manifest){$evidencePaths+=@($call.request,$call.response)}
    foreach($path in $evidencePaths){
        $entry=Get-Item -LiteralPath $path
        while($entry){if($entry.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'REPARSE_DISCOVERY_PATH'};$entry=$entry.Parent}
        $sourceHandles+=[IO.File]::Open($path,'Open','Read','Read')
    }
    Invoke-Policy @('validate-local')
    if ($Stage -eq 'Retire' -and (-not $VerificationReceipt -or -not $ExpectedVerificationReceiptSha256)) { throw 'VERIFICATION_RECEIPT_REQUIRED' }
    $primary = [IO.Path]::GetFullPath((Join-Path $ProjectsRoot 'lotus-platform/automation/CanonicalRuntimeReservation.psm1'))
    foreach ($path in @($primary, $Disposition, $Plan, $Inventory)) {
        $entry = Get-Item -LiteralPath $path
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'REPARSE_PATH_REFUSED' }
        if ($entry -is [IO.FileInfo]) { $entry = $entry.Directory }
        while ($entry) {
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'REPARSE_PATH_REFUSED' }
            $entry = $entry.Parent
        }
    }
    $script:authority = Import-Module -Name $primary -PassThru -Scope Local
    if ($script:authority.Count -ne 1 -or $script:authority.Path -ne $primary) { throw 'PRIMARY_MODULE_REQUIRED' }
    # Qualified module invocation prevents a competing exported function from becoming authority.
    try { $script:operation = & $script:authority {
        param($root, $holder, $workbench)
        Enter-CanonicalRuntimeOperation -ProjectsRoot $root -Holder $holder -WorkbenchRepoPath $workbench
    } $ProjectsRoot $RuntimeHolder $WorkbenchRepoPath
    } catch {
        if ($LASTEXITCODE -ne 0) { $script:nativeStatus = $LASTEXITCODE }
        throw
    }
    if ($IsWindows -or $env:OS -eq 'Windows_NT') {
        $acl = Get-Acl -LiteralPath $script:approval.archive_root
        $allowed = @([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544')
        foreach ($rule in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])) {
            if ($rule.AccessControlType -eq 'Allow' -and $allowed -notcontains $rule.IdentityReference.Value) { throw 'PRIVATE_ARCHIVE_STORAGE_REQUIRED' }
        }
    }
    $runId = [guid]::NewGuid().ToString('N')
    $script:runId=$runId
    $runDirectory = Join-Path $script:approval.archive_root "runs/$runId"
    New-Item -ItemType Directory -Path $runDirectory | Out-Null
    $script:receiptPath = Join-Path $runDirectory 'receipt.json'
    $script:journal = @{ schema_version='lotus.resource-recovery.receipt.v1'; status='operation_admitted'; stage=$Stage;
        approval_sha256=$ExpectedDispositionSha256; operation_token=$script:operation.Token;
        primary_head=$script:approval.primary_head; helper_files=$script:approval.helper_files;
        targets=@(); remaining_targets=@($script:approval.targets); helper_resources=@();admissions=@();
        evidence_class='test_execution'; production_acceptance=$false }
    Save-Journal
    Assert-Admission
    $archiveIdentity = if ($script:approval.schema_version -eq 'lotus.resource-recovery.retirement.v2') {
        $script:approval.archive_approval_sha256
    } else { $ExpectedDispositionSha256 }
    $script:journal.archive_approval_sha256 = $archiveIdentity
    $script:journal.archive_receipt_sha256 = $ExpectedVerificationReceiptSha256
    $archiveDirectory = Join-Path $script:approval.archive_root "$archiveIdentity/archives"
    if ($Stage -eq 'DryRun') {
        $prepared = Prepare-Current $runDirectory 'dry-run'
        $script:journal.status = 'dry_run_ready'
    } elseif ($Stage -eq 'ArchiveVerify') {
        if (Test-Path -LiteralPath $archiveDirectory) { throw 'ARCHIVE_ALREADY_EXISTS_PRESERVE' }
        New-Item -ItemType Directory -Path $archiveDirectory | Out-Null
        $prepared = Prepare-Current $archiveDirectory 'archive-verify'
        $index = 0
        foreach ($item in $prepared.targets) {
            $directory = Join-Path $archiveDirectory ([string]$index)
            New-Item -ItemType Directory -Path $directory | Out-Null
            $script:journal.targets += @{ kind=$item.target.kind; id=$item.target.id; status='archival_requested' }
            Save-Journal
            # Fresh observations precede each target's archive, not just the first target.
            $null = Prepare-Current $archiveDirectory 'archive-verify' $index
            Archive-Target $item $directory $index
            $script:journal.targets[-1].status = 'archive_and_isolated_restore_completed'
            Save-Journal
            $index++
        }
        Invoke-Policy @('verify','--directory',$archiveDirectory)
        $script:journal.verification_sha256 = (Get-FileHash -LiteralPath (Join-Path $archiveDirectory 'verification.json') -Algorithm SHA256).Hash.ToLowerInvariant()
        $script:journal.status = 'verification_completed_pending_finish'
    } else {
        # Fresh authority evidence must never overwrite immutable archive provenance.
        $null = Prepare-Current $runDirectory 'retire'
        Invoke-Policy @('verify-retirement','--directory',$archiveDirectory,'--receipt',$VerificationReceipt,'--expected-receipt-sha256',$ExpectedVerificationReceiptSha256)
        $index = 0
        foreach ($target in $script:approval.targets) {
            $script:journal.targets += @{kind=$target.kind; id=$target.id; status='retirement_requested'}
            Save-Journal
            Invoke-Policy @('verify-retirement','--directory',$archiveDirectory,'--receipt',$VerificationReceipt,'--expected-receipt-sha256',$ExpectedVerificationReceiptSha256)
            # Potentially expensive archive verification cannot age the final
            # target/consumer observation made immediately before normal removal.
            $null = Prepare-Current $runDirectory 'retire' $index
            Assert-LiveAction $index
            Invoke-RecoveryDocker $script:approval.source_context @($target.kind,'rm',$target.id) -LiveTargetIndex $index | Out-Null
            $remaining = if ($target.kind -eq 'image') {
                @(Invoke-RecoveryDocker $script:approval.source_context @('image','ls','--all','--quiet','--no-trunc'))
            } else {
                @(Invoke-RecoveryDocker $script:approval.source_context @('volume','ls','--quiet'))
            }
            if ($remaining -contains $target.id) { throw 'RETIREMENT_NOT_CONFIRMED' }
            $script:journal.targets[-1].status = 'native_removal_absence_confirmed'
            $script:journal.remaining_targets = @($script:journal.remaining_targets | Where-Object { -not ($_.kind -eq $target.kind -and $_.id -eq $target.id) })
            Save-Journal
            $index++
        }
        $script:journal.status = 'retirement_completed_pending_finish'
    }
    Save-Journal
    $exitStatus = 0
} catch {
    $exitStatus = if ($script:nativeStatus -ne 0) { $script:nativeStatus } else { 1 }
    $reason = Get-SafeRecoveryReason $_.Exception.Message 'RESOURCE_RECOVERY_FAILED'
    if ($script:journal) { $script:journal.status = 'failed_or_interrupted'; $script:journal.reason = $reason; Save-Journal }
    Write-Output $reason
} finally {
    if ($script:operation) {
        try {
            $outcome = if ($exitStatus -eq 0) { 'success' } else { 'failure' }
            & $script:authority { param($op,$result); Exit-CanonicalRuntimeOperation -Operation $op -Outcome $result } $script:operation $outcome | Out-Null
            if ($exitStatus -eq 0) {
                $script:journal.status = switch ($Stage) { 'DryRun' {'dry_run_ready'} 'ArchiveVerify' {'archive_verified'} 'Retire' {'retired'} }
            }
        } catch {
            if ($exitStatus -eq 0) { $exitStatus = 1 }
            if ($script:journal) { $script:journal.status = 'operation_finish_failed' }
        }
    }
    foreach ($stream in $sourceHandles) { $stream.Dispose() }
    if ($script:journal) { Save-Journal }
}
Write-Output "Resource recovery exit=$exitStatus; receipt=$script:receiptPath"
exit $exitStatus
