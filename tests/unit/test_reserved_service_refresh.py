"""Native PowerShell boundary proof; every Docker/Python call is a controlled fake."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from automation.canonical_runtime_lease import digest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('case', ['missing', 'foreign', 'digest', 'foreign-context', 'port-drift', 'build-failure', 'image-source', 'up-failure', 'readiness', 'success',
                                'external-compose', 'untracked-compose', 'dirty-compose', 'env-compose', 'preview', 'preview-digest', 'preview-context',
                                'tracked-compose', 'ignored-compose', 'reparse-compose', 'mismatched-project', 'preview-mismatched-project',
                                'ancestor-context', 'ancestor-dockerfile', 'preview-ancestor-context',
                                'ignored-context', 'preview-ignored-context', 'shell-config', 'env-config', 'preview-env-config'])
def test_shipped_reserved_refresh_keeps_fence_and_bounds_mutation(tmp_path, case):
    project = tmp_path / 'other/lotus-gateway' if case in {'mismatched-project', 'preview-mismatched-project'} else tmp_path / 'lotus-gateway'
    project.mkdir(parents=True)
    (project / 'compose.yaml').write_text('services: {}', encoding='utf-8')
    (project / 'Dockerfile').write_text('FROM scratch', encoding='utf-8')
    (project / '.gitignore').write_text('ignored.yaml\nignored-link/\nsecret.bin\n', encoding='utf-8')
    (project / 'reviewed.yaml').write_text('services: {}', encoding='utf-8')
    for args in (['init'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', '-c', 'commit.gpgsign=false', 'commit', '-m', 'fixture']):
        subprocess.run(['git', '-C', str(project), *args], check=True, capture_output=True)
    admitted_project = tmp_path / 'lotus-gateway'
    revision = subprocess.check_output(['git', '-C', str(project), 'rev-parse', 'HEAD'], text=True).strip()
    if project != admitted_project:
        subprocess.run(['git', 'clone', str(project), str(admitted_project)], check=True, capture_output=True)
    extra = tmp_path / 'external.yaml' if case in {'external-compose', 'env-compose'} else project / 'untracked.yaml'
    extra.write_text('services: {}', encoding='utf-8')
    if case == 'tracked-compose': extra = project / 'reviewed.yaml'
    if case == 'ignored-compose':
        extra = project / 'ignored.yaml'
        extra.write_text('services: {}', encoding='utf-8')
    if case == 'reparse-compose':
        link = project / 'redirect'
        if os.name == 'nt':
            subprocess.run([shutil.which('pwsh'), '-NoProfile', '-Command',
                            f"New-Item -ItemType Junction -Path '{link}' -Target '{tmp_path}' | Out-Null"],
                           check=True, capture_output=True)
        else:
            link.symlink_to(tmp_path, target_is_directory=True)
        extra = link / 'external.yaml'
        (tmp_path / 'external.yaml').write_text('services: {}', encoding='utf-8')
    if case == 'dirty-compose':
        (project / 'compose.yaml').write_text('services: {changed: {}}', encoding='utf-8')
    if case in {'ignored-context', 'preview-ignored-context'}:
        (project / 'secret.bin').write_text('UNREVIEWED_BUILD_PAYLOAD', encoding='utf-8')
    if case in {'ancestor-context', 'ancestor-dockerfile', 'preview-ancestor-context'}:
        external = tmp_path / 'foreign-build'
        (external / 'subdir').mkdir(parents=True)
        (external / 'subdir/Dockerfile').write_text('FROM scratch', encoding='utf-8')
        link = project / 'ignored-link'
        if os.name == 'nt':
            subprocess.run([shutil.which('pwsh'), '-NoProfile', '-Command',
                            f"New-Item -ItemType Junction -Path '{link}' -Target '{external}' | Out-Null"],
                           check=True, capture_output=True)
        else:
            link.symlink_to(external, target_is_directory=True)
    book = tmp_path / 'lotus-platform/output/canonical-runtime/reservations.v1.json'
    book.parent.mkdir(parents=True)
    book.write_text('{}', encoding='utf-8')  # Presence alone must select the admission path.
    plan = {'services': [{'repository': 'lotus-gateway', 'project': 'gateway', 'service': 'lotus-gateway'}],
            'targetScope': {'projects': {'gateway': str(admitted_project).replace('\\', '/').lower()},
                            'sources': {'lotus-gateway': revision}}}
    evaluated = {'name': 'gateway', 'services': {'lotus-gateway': {
        'build': {'context': str(project), 'dockerfile': 'Dockerfile', 'args': {'APP_GIT_COMMIT_SHA': revision, 'APP_GIT_BRANCH': 'main'}},
        'command': ['echo', '$$RUNTIME_VALUE'], 'environment': {'REVIEWED': 'approved'},
        'ports': [{'published': 8111}]}}}
    plan['composeConfigDigest'] = digest(evaluated)
    evaluated_path = tmp_path / 'evaluated.json'
    evaluated_path.write_text(json.dumps(evaluated), encoding='utf-8')
    plan_path = tmp_path / 'plan.json'
    plan_path.write_text(json.dumps(plan), encoding='utf-8')
    log = tmp_path / 'calls.txt'
    lock = book.parent / 'operation.lock'
    command = f"""
$ErrorActionPreference='Stop'
$global:case='{case}'
function global:Assert-Fenced {{
  $contended=$false
  try {{ $probe=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); $probe.Dispose() }}
  catch [IO.IOException] {{ $contended=$true }}
  if (-not $contended) {{ throw 'IO_OUTSIDE_OPERATION_FENCE' }}
}}
function global:python {{
  if ($args[0] -like '*canonical_refresh_inputs.py') {{ & '{sys.executable}' @args; return }}
  Assert-Fenced
  $action=$args[1]
  Add-Content -LiteralPath '{log}' -Value "lease:$action"
  $global:LASTEXITCODE=0
  if ($action -in @('begin-refresh','preview-refresh')) {{
    if ($global:case -in @('foreign','digest','preview-digest')) {{ $global:LASTEXITCODE=1; return 'CONTROLLED_ADMISSION_REFUSAL' }}
    $plan=Get-Content -LiteralPath '{plan_path}' -Raw | ConvertFrom-Json
    return (@{{operation=@{{token='reviewed-token'; refresh=@{{plan=$plan;originalResources=@(@{{id='old';project='gateway';service='lotus-gateway'}})}}}}; bindings=@(@{{id='old';ports=@(8111)}}); scope=@{{}}}} | ConvertTo-Json -Depth 12 -Compress)
  }}
  if ($action -eq 'prepare-refresh') {{
    if ($global:case -eq 'image-source') {{ $global:LASTEXITCODE=1; return 'CONTROLLED_SOURCE_IMAGE_REFUSAL' }}
    $refsPath=$args[[Array]::IndexOf($args,'--prepared-images')+1]
    $refs=@(Get-Content -LiteralPath $refsPath -Raw | ConvertFrom-Json)
    if ($refs.Count -ne 1 -or $refs[0].reference -ne 'lotus-reserved-refresh:reviewed-token-lotus-gateway') {{ throw 'UNBOUNDED_IMAGE_REFS' }}
    return (@{{operation=@{{refresh=@{{preparedImages=@(@{{service='lotus-gateway';imageId='sha256:{'c' * 64}'}})}}}}}} | ConvertTo-Json -Depth 8 -Compress)
  }}
  if ($action -eq 'finish-refresh') {{
    $outcome=$args[[Array]::IndexOf($args,'--outcome')+1]
    Add-Content -LiteralPath '{log}' -Value "outcome:$outcome"
  }}
  return '{{}}'
}}
function global:ReservedFakeDocker {{
  Assert-Fenced
  $line=$args -join ' '
  Add-Content -LiteralPath '{log}' -Value "docker:$line"
  $global:LASTEXITCODE=0
  if ($args -contains 'config') {{
    $context=if ($global:case -in @('foreign-context','preview-context')) {{ '{tmp_path}' }} else {{ '{project}' }}
    if ($global:case -in @('ancestor-context','preview-ancestor-context')) {{ $context='{project / 'ignored-link/subdir'}' }}
    $dockerfile=if ($global:case -eq 'ancestor-dockerfile') {{ 'ignored-link/subdir/Dockerfile' }} else {{ 'Dockerfile' }}
    $port=if ($global:case -eq 'port-drift') {{ 9999 }} else {{ 8111 }}
    $model=Get-Content -LiteralPath '{evaluated_path}' -Raw | ConvertFrom-Json
    $model.services.'lotus-gateway'.build.context=$context
    $model.services.'lotus-gateway'.build.dockerfile=$dockerfile
    $model.services.'lotus-gateway'.ports[0].published=$port
    if ($global:case -eq 'shell-config') {{ $model.services.'lotus-gateway'.build.args.APP_GIT_BRANCH='unreviewed' }}
    if ($global:case -in @('env-config','preview-env-config')) {{ $model.services.'lotus-gateway'.environment.REVIEWED='unreviewed' }}
    return ($model | ConvertTo-Json -Compress -Depth 8)
  }}
  if ($args -contains 'build') {{
    if ($global:case -eq 'build-failure') {{ $global:LASTEXITCODE=23 }}
    $i=[Array]::LastIndexOf($args,'-f')
    $override=Get-Content -LiteralPath $args[$i+1] -Raw | ConvertFrom-Json
    if ($override.services.'lotus-gateway'.build.labels.'org.opencontainers.image.revision' -ne '{revision}') {{ throw 'BUILD_SOURCE_MISSING' }}
    $first=[Array]::IndexOf($args,'-f')
    $frozen=Get-Content -LiteralPath $args[$first+1] -Raw | ConvertFrom-Json
    $build=$frozen.services.'lotus-gateway'.build
    if ($build.context -eq '{project}' -or (Test-Path (Join-Path $build.context 'secret.bin')) -or (Test-Path (Join-Path $build.context 'untracked.yaml'))) {{ throw 'UNREVIEWED_BUILD_CONTEXT' }}
    if ((Get-Content -LiteralPath $build.dockerfile -Raw) -ne 'FROM scratch') {{ throw 'COMMITTED_DOCKERFILE_MISSING' }}
    if ($build.args.APP_GIT_COMMIT_SHA -ne '{revision}' -or $build.args.APP_GIT_BRANCH -ne 'main') {{ throw 'BUILD_METADATA_CHANGED' }}
    if ($frozen.services.'lotus-gateway'.command[1] -ne '$$RUNTIME_VALUE') {{ throw 'LITERAL_DOLLAR_NOT_ESCAPED' }}
    if ($args[[Array]::IndexOf($args,'--project-directory')+1] -ne '{project}') {{ throw 'COMPOSE_CHECKOUT_PROVENANCE_CHANGED' }}
    return
  }}
  if ($args -contains 'up') {{
    if ($line -notlike '*up -d --no-deps --no-build --pull never lotus-gateway') {{ throw 'UNBOUNDED_REPLACEMENT' }}
    $i=[Array]::LastIndexOf($args,'-f')
    $override=Get-Content -LiteralPath $args[$i+1] -Raw | ConvertFrom-Json
    if ($override.services.'lotus-gateway'.image -ne 'sha256:{'c' * 64}') {{ throw 'MUTABLE_IMAGE_REPLACEMENT' }}
    if ($global:case -eq 'up-failure') {{ $global:LASTEXITCODE=31 }}
    return
  }}
  if ($args -contains 'ps') {{
    $state=if ($global:case -eq 'readiness') {{ 'exited' }} else {{ 'running' }}
    return (@{{Service='lotus-gateway';State=$state;Health='healthy';Publishers=@(@{{TargetPort=8000;PublishedPort=8111}})}} | ConvertTo-Json -Compress -Depth 4)
  }}
  throw 'UNEXPECTED_DOCKER_COMMAND'
}}
{"$env:COMPOSE_FILE='" + str(extra) + "'" if case == 'env-compose' else ''}
& '{ROOT / 'automation/Service-Refresh.ps1'}' -ProjectPath '{project}' -ProjectsRoot '{tmp_path}' `
  -Services lotus-gateway -DockerCommand ReservedFakeDocker -HealthTimeoutSeconds 0 `
  {'' if case == 'missing' else f"-RuntimeHolder owner -RefreshPlan '{plan_path}' -RefreshPlanDigest sha256:reviewed"} `
  {f"-ComposeFiles '{extra}'" if case in {'external-compose', 'untracked-compose', 'tracked-compose', 'ignored-compose', 'reparse-compose'} else ''} {'-DryRun' if case.startswith('preview') else ''}
"""
    shell = shutil.which('pwsh') or shutil.which('powershell')
    assert shell
    result = subprocess.run([shell, '-NoProfile', '-Command', command], text=True, capture_output=True, timeout=30)
    calls = log.read_text(encoding='utf-8-sig').splitlines() if log.exists() else []
    assert 'IO_OUTSIDE_OPERATION_FENCE' not in result.stderr
    docker = [row for row in calls if row.startswith('docker:') and ' config ' not in row]
    if case.startswith('preview'):
        assert result.returncode == (0 if case in {'preview', 'preview-ignored-context'} else 1), result.stdout + result.stderr
        assert docker == []
        assert 'lease:begin-refresh' not in calls and 'lease:finish-refresh' not in calls
        assert book.read_text(encoding='utf-8') == '{}'
        if case == 'preview':
            assert 'up -d --no-deps --no-build --pull never' in result.stdout
            assert 'up -d --build' not in result.stdout
    elif case in {'missing', 'foreign', 'digest'}:
        assert result.returncode == 1, result.stdout + result.stderr
        assert docker == []
    elif case in {'build-failure', 'image-source'}:
        assert result.returncode == 1, result.stdout + result.stderr
        assert len(docker) == 1 and ' build lotus-gateway' in docker[0]
        assert calls[-1] == 'outcome:failure'
    elif case in {'foreign-context', 'port-drift', 'external-compose', 'untracked-compose', 'dirty-compose', 'env-compose', 'ignored-compose', 'reparse-compose', 'mismatched-project', 'ancestor-context', 'ancestor-dockerfile', 'shell-config', 'env-config'}:
        assert result.returncode == 1, result.stdout + result.stderr
        assert docker == []
        assert calls[-1] == 'outcome:failure'
    else:
        assert sum(' up ' in row for row in docker) == 1
        assert sum(' build ' in row for row in docker) == 1
        assert result.returncode == (0 if case in {'success', 'tracked-compose', 'ignored-context'} else 1), result.stdout + result.stderr
        assert calls[-1] == ('outcome:success' if case in {'success', 'tracked-compose', 'ignored-context'} else 'outcome:failure')
    if case in {'shell-config', 'env-config', 'preview-env-config'}:
        assert 'Reviewed Compose digest or committed build snapshot validation failed' in result.stderr
    if case in {'mismatched-project', 'preview-mismatched-project'}:
        assert 'ProjectPath differs from the checkout admitted' in result.stderr
        assert not any(row.startswith('docker:') for row in calls)
    if case in {'ancestor-context', 'ancestor-dockerfile', 'preview-ancestor-context'}:
        assert 'reparse point or ancestor' in result.stderr
    # The adapter releases the actual exclusive handle even on refusal/failure.
    if lock.exists():
        probe = subprocess.run([shell, '-NoProfile', '-Command',
                                f"$f=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); $f.Dispose()"],
                               capture_output=True, text=True, timeout=15)
        assert probe.returncode == 0, probe.stderr
