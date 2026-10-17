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


@pytest.mark.parametrize('case,refusal', [
    ('success', None), ('multiple', None), ('preview', None), ('windows-preview', None),
    ('preview-ambiguous', 'exactly one build owner'),
    ('zero', 'exactly one build owner'), ('ambiguous', 'exactly one build owner'),
    ('mismatch', 'exactly one build owner'), ('missing-image', 'explicit shared image'),
    ('inline', 'local owned context'), ('additional', 'local owned context'),
    ('tags', 'additional image tags'),
    ('auxiliary-secrets', 'Reserved build cannot use auxiliary secrets or SSH inputs'),
    ('auxiliary-ssh', 'Reserved build cannot use auxiliary secrets or SSH inputs'),
    ('direct-secrets', 'Reserved build cannot use auxiliary secrets or SSH inputs'),
    ('direct-ssh', 'Reserved build cannot use auxiliary secrets or SSH inputs'),
    ('foreign-context', 'outside its reviewed repository'),
    ('foreign-dockerfile', 'outside its reviewed repository'),
    ('ancestor-context', 'reparse point or ancestor'),
    ('missing-dockerfile', 'Build context and Dockerfile must exist'),
    ('unresolved-arg', 'Evaluated Compose must resolve'), ('unresolved-env', 'Evaluated Compose must resolve'),
    ('digest-owner', 'differs from reviewed digest'),
    ('build-failure', 'Reserved build failed'), ('image-source', 'CONTROLLED_IMAGE_SOURCE_REFUSAL'),
])
def test_shared_builder_does_not_expand_replacement_or_execute_dependencies(tmp_path, case, refusal):
    preview = case in {'preview', 'windows-preview', 'preview-ambiguous'}
    project = tmp_path / 'lotus-idea'
    project.mkdir()
    for name, content in {'compose.yaml': 'services: {}', 'Dockerfile': 'FROM scratch',
                          '.gitignore': 'secret.bin\nredirect/\n'}.items():
        (project / name).write_text(content, encoding='utf-8')
    for args in (['init'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                                       '-c', 'commit.gpgsign=false', 'commit', '-m', 'fixture']):
        subprocess.run(['git', '-C', str(project), *args], check=True, capture_output=True)
    revision = subprocess.check_output(['git', '-C', str(project), 'rev-parse', 'HEAD'], text=True).strip()
    (project / 'secret.bin').write_text('ignored input must not be built', encoding='utf-8')
    (project / 'untracked').write_text('untracked input must not be built', encoding='utf-8')
    # The snapshot must use committed bytes, even if working bytes are different.
    (project / 'Dockerfile').write_text('unreviewed bytes', encoding='utf-8')
    selected = ['lotus-idea', 'worker'] if case == 'multiple' else ['lotus-idea']
    owner = 'lotus-idea-migrations'
    model = {'name': 'idea', 'services': {
        'lotus-idea': {'image': 'lotus-idea:local', 'ports': [{'published': 8330}],
                       'depends_on': {owner: {'condition': 'service_completed_successfully'}},
                       'environment': {'TOKEN': '$$literal'}},
        'worker': {'image': 'lotus-idea:local', 'depends_on': {owner: {'condition': 'service_completed_successfully'}}},
        owner: {'image': 'lotus-idea:local', 'build': {'context': str(project), 'dockerfile': 'Dockerfile',
                'args': {'GIT_COMMIT_SHA': revision}}, 'command': ['python', 'run_migrations.py'],
                'depends_on': {'postgres': {'condition': 'service_healthy'}}},
        'postgres': {'image': 'postgres:18-alpine'}}}
    if case == 'zero': del model['services'][owner]['build']
    if case in {'ambiguous', 'preview-ambiguous'}: model['services']['duplicate'] = dict(model['services'][owner])
    if case == 'mismatch': model['services'][owner]['image'] = 'lotus-idea:other'
    if case == 'missing-image': del model['services']['lotus-idea']['image']
    if case == 'inline': model['services'][owner]['build']['dockerfile_inline'] = 'FROM scratch'
    if case == 'additional': model['services'][owner]['build']['additional_contexts'] = {'foreign': str(tmp_path)}
    if case == 'tags': model['services'][owner]['build']['tags'] = ['lotus-idea:local']
    if case.startswith(('auxiliary-', 'direct-')):
        builder = owner
        if case.startswith('direct-'):
            builder = 'lotus-idea'
            model['services'][builder]['build'] = model['services'][owner].pop('build')
        field = 'secrets' if case.endswith('secrets') else 'ssh'
        model['services'][builder]['build'][field] = ['SYNTHETIC_AUXILIARY_AUTHORITY']
        model['secrets'] = {'SYNTHETIC_AUXILIARY_AUTHORITY': {'file': 'SYNTHETIC_HOST_PATH'}}
    if case == 'foreign-context': model['services'][owner]['build']['context'] = str(tmp_path)
    if case == 'foreign-dockerfile': model['services'][owner]['build']['dockerfile'] = str(tmp_path / 'foreign')
    if case == 'missing-dockerfile': model['services'][owner]['build']['dockerfile'] = 'untracked'
    if case == 'unresolved-arg': model['services'][owner]['build']['args']['GIT_COMMIT_SHA'] = None
    if case == 'unresolved-env': model['services']['lotus-idea']['environment']['TOKEN'] = None
    if case == 'ancestor-context':
        foreign = tmp_path / 'foreign'
        foreign.mkdir()
        (foreign / 'Dockerfile').write_text('FROM scratch', encoding='utf-8')
        link = project / 'redirect'
        if os.name == 'nt':
            subprocess.run([shutil.which('pwsh'), '-NoProfile', '-Command',
                            f"New-Item -ItemType Junction -Path '{link}' -Target '{foreign}' | Out-Null"],
                           check=True, capture_output=True)
        else:
            link.symlink_to(foreign, target_is_directory=True)
        model['services'][owner]['build']['context'] = str(link)
    plan = {'services': [{'repository': 'lotus-idea', 'project': 'idea', 'service': name} for name in selected],
            'targetScope': {'projects': {'idea': str(project).replace('\\', '/').lower()},
                            'sources': {'lotus-idea': revision}}, 'composeConfigDigest': digest(model)}
    if case == 'digest-owner': model['services'][owner]['build']['args']['GIT_COMMIT_SHA'] = 'unreviewed'
    model_path = tmp_path / 'model.json'
    model_path.write_text(json.dumps(model), encoding='utf-8')
    plan_path = tmp_path / 'plan.json'
    plan_path.write_text(json.dumps(plan), encoding='utf-8')
    book = tmp_path / 'lotus-platform/output/canonical-runtime/reservations.v1.json'
    book.parent.mkdir(parents=True)
    book.write_text('{}', encoding='utf-8')
    lock = book.parent / 'operation.lock'
    log = tmp_path / 'calls.txt'
    command = f"""
$ErrorActionPreference='Stop'
function global:Assert-Fenced {{
  $contended=$false
  try {{ $probe=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); $probe.Dispose() }} catch [IO.IOException] {{ $contended=$true }}
  if (-not $contended) {{ throw 'IO_OUTSIDE_OPERATION_FENCE' }}
}}
function global:python {{
  Assert-Fenced
  if ($args[0] -like '*canonical_refresh_inputs.py') {{ & '{sys.executable}' @args; return }}
  $global:LASTEXITCODE=0
  $action=$args[1]; Add-Content -LiteralPath '{log}' -Value "lease:$action"
  $plan=Get-Content -LiteralPath '{plan_path}' -Raw | ConvertFrom-Json
  if ($action -in @('begin-refresh','preview-refresh')) {{
    $resources=@($plan.services | ForEach-Object {{ @{{id=$_.service;project='idea';service=$_.service}} }})
    $bindings=@($plan.services | ForEach-Object {{ @{{id=$_.service;ports=if ($_.service -eq 'lotus-idea') {{ @(8330) }} else {{ @() }} }} }})
    return (@{{operation=@{{token='reviewed-token';refresh=@{{plan=$plan;originalResources=$resources}}}};bindings=$bindings;scope=@{{}}}} | ConvertTo-Json -Depth 12 -Compress)
  }}
  if ($action -eq 'prepare-refresh') {{
    if ('{case}' -eq 'image-source') {{ $global:LASTEXITCODE=1; return 'CONTROLLED_IMAGE_SOURCE_REFUSAL' }}
    $refs=@(Get-Content -LiteralPath $args[[Array]::IndexOf($args,'--prepared-images')+1] -Raw | ConvertFrom-Json)
    if ($refs.Count -ne $plan.services.Count) {{ throw 'PREPARED_OWNER_EXPANDED_SCOPE' }}
    foreach ($ref in $refs) {{
      if ($ref.service -notin $plan.services.service -or $ref.reference -ne 'lotus-reserved-refresh:reviewed-token-{owner}') {{ throw 'WRONG_PREPARED_CONSUMER_OR_IMAGE' }}
    }}
    $images=@($plan.services | ForEach-Object {{ @{{service=$_.service;imageId='sha256:{'c' * 64}'}} }})
    return (@{{operation=@{{refresh=@{{preparedImages=$images}}}}}} | ConvertTo-Json -Depth 12 -Compress)
  }}
  if ($action -eq 'finish-refresh') {{ Add-Content -LiteralPath '{log}' -Value ('outcome:'+$args[[Array]::IndexOf($args,'--outcome')+1]) }}
  return '{{}}'
}}
function global:SharedFakeDocker {{
  Assert-Fenced; $global:LASTEXITCODE=0
  Add-Content -LiteralPath '{log}' -Value ('docker:'+($args -join ' '))
  if ($args -contains 'config') {{ return Get-Content -LiteralPath '{model_path}' -Raw }}
  if ($args -contains 'build') {{
    if ($args[-1] -ne '{owner}' -or $args[-2] -ne 'build' -or $args -contains '--with-dependencies') {{ throw 'BUILD_OWNER_NOT_DEDUPLICATED' }}
    $override=Get-Content -LiteralPath $args[[Array]::LastIndexOf($args,'-f')+1] -Raw | ConvertFrom-Json
    if ($override.services.'{owner}'.image -ne 'lotus-reserved-refresh:reviewed-token-{owner}') {{ throw 'ORIGINAL_SHARED_TAG_MOVED' }}
    if ($override.services.'{owner}'.build.labels.'org.opencontainers.image.revision' -ne '{revision}') {{ throw 'BUILD_SOURCE_MISSING' }}
    foreach ($consumer in @({','.join(repr(s) for s in selected)})) {{
      if ($override.services.($consumer).build) {{ throw 'DUPLICATE_SHARED_IMAGE_WRITER' }}
    }}
    $frozen=Get-Content -LiteralPath $args[[Array]::IndexOf($args,'-f')+1] -Raw | ConvertFrom-Json
    $build=$frozen.services.'{owner}'.build
    if ($build.context -eq '{project}' -or (Test-Path (Join-Path $build.context 'secret.bin')) -or (Test-Path (Join-Path $build.context 'untracked'))) {{ throw 'UNREVIEWED_BUILD_BYTES' }}
    if ((Get-Content -LiteralPath $build.dockerfile -Raw) -ne 'FROM scratch' -or $build.args.GIT_COMMIT_SHA -ne '{revision}') {{ throw 'COMMITTED_BUILD_INPUT_MISSING' }}
    if ('{case}' -eq 'build-failure') {{ $global:LASTEXITCODE=23 }}
    return
  }}
  if ($args -contains 'up') {{
    if (($args -join ' ') -notlike '*up -d --no-deps --no-build --pull never {' '.join(selected)}') {{ throw 'DEPENDENCY_OR_OWNER_EXECUTION' }}
    $override=Get-Content -LiteralPath $args[[Array]::LastIndexOf($args,'-f')+1] -Raw | ConvertFrom-Json
    foreach ($consumer in @({','.join(repr(s) for s in selected)})) {{
      if ($override.services.($consumer).image -ne 'sha256:{'c' * 64}') {{ throw 'UNPINNED_CONSUMER' }}
    }}
    return
  }}
  if ($args -contains 'ps') {{ return ConvertTo-Json -InputObject @({','.join("@{Service='" + s + "';State='running';Health='healthy';Publishers=" + ("@(@{PublishedPort=8330})" if s == 'lotus-idea' else '@()') + "}" for s in selected)}) -Depth 8 -Compress }}
  throw 'UNEXPECTED_DOCKER_COMMAND'
}}
& '{ROOT / 'automation/Service-Refresh.ps1'}' -ProjectPath '{project}' -ProjectsRoot '{tmp_path}' `
  -Services @({','.join(repr(s) for s in selected)}) -DockerCommand SharedFakeDocker -HealthTimeoutSeconds 0 `
  -RuntimeHolder owner -RefreshPlan '{plan_path}' -RefreshPlanDigest sha256:reviewed {'-DryRun' if preview else ''}
"""
    shell = shutil.which('powershell') if case == 'windows-preview' else shutil.which('pwsh') or shutil.which('powershell')
    if case == 'windows-preview' and shell is None:
        pytest.skip('Windows PowerShell is unavailable')
    assert shell
    result = subprocess.run([shell, '-NoProfile', '-Command', command], capture_output=True, text=True, timeout=30)
    calls = log.read_text(encoding='utf-8-sig').splitlines()
    builds = [line for line in calls if ' build ' in line]
    ups = [line for line in calls if ' up ' in line]
    if case.startswith(('auxiliary-', 'direct-')):
        assert builds == ups == [], calls
    assert 'IO_OUTSIDE_OPERATION_FENCE' not in result.stderr
    assert 'SYNTHETIC_AUXILIARY_AUTHORITY' not in result.stdout + result.stderr
    assert 'SYNTHETIC_HOST_PATH' not in result.stdout + result.stderr
    assert result.returncode == (1 if refusal else 0), result.stdout + result.stderr
    if refusal:
        assert refusal in result.stderr, result.stdout + result.stderr
        assert not ups
        if preview:
            assert 'lease:finish-refresh' not in calls and 'lease:begin-refresh' not in calls
        else:
            assert 'lease:finish-refresh' in calls and calls[-1] == 'outcome:failure'
        assert len(builds) == (1 if case in {'build-failure', 'image-source'} else 0)
    elif preview:
        assert not builds and not ups
        assert 'Build owners: lotus-idea-migrations; replacement services: lotus-idea' in result.stdout
        assert 'lease:begin-refresh' not in calls and 'lease:finish-refresh' not in calls
    else:
        assert len(builds) == len(ups) == 1
        assert calls.index(builds[0]) < calls.index('lease:prepare-refresh') < calls.index(ups[0])
        assert calls[-1] == 'outcome:success'
    assert book.read_text(encoding='utf-8') == '{}'


@pytest.mark.parametrize('case', ['success', 'running-success', 'created-success', 'timeout', 'nonzero', 'oom', 'restart',
                                'missing', 'duplicate', 'malformed', 'truncated-id', 'project-drift', 'image-drift', 'source-drift',
                                'container-drift', 'inspect-failure', 'inspect-duplicate', 'inspect-malformed',
                                'restart-policy', 'prepare-missing', 'prepare-duplicate',
                                'readiness-only-oneoff-before', 'readiness-only-oneoff-after', 'only-oneoff', 'duplicate-real',
                                'missing-oneoff', 'malformed-oneoff', 'boolean-oneoff', 'case-oneoff',
                                'stale-missing-oneoff', 'stale-identity-drift',
                                'acquired-two', 'acquired-none', 'acquired-only-run', 'acquired-malformed-id',
                                'acquired-missing-oneoff', 'acquired-malformed-oneoff', 'acquired-foreign-project',
                                'acquired-foreign-service', 'acquired-wrong-id', 'acquired-inspect-failure',
                                'acquired-inspect-duplicate', 'acquired-inspect-malformed'])
def test_core_migration_completes_before_ten_application_replacements(tmp_path, case):
    # Native call-boundary proof only. Non-acquired readiness observations are not real finish proof;
    # production begin/prepare/finish accounting is exercised in test_canonical_runtime_refresh.py.
    project = tmp_path / 'lotus-core'
    project.mkdir()
    (project / 'compose.yaml').write_text('services: {}', encoding='utf-8')
    (project / 'Dockerfile').write_text('FROM scratch', encoding='utf-8')
    for args in (['init'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                                       '-c', 'commit.gpgsign=false', 'commit', '-m', 'fixture']):
        subprocess.run(['git', '-C', str(project), *args], check=True, capture_output=True)
    revision = subprocess.check_output(['git', '-C', str(project), 'rev-parse', 'HEAD'], text=True).strip()
    core = next(repo for repo in json.loads((ROOT / 'automation/service-map.json').read_text())['repos'] if repo['name'] == 'lotus-core')
    services = next(rule['services'] for rule in core['rules'] if 'alembic/' in rule['pathPrefixes'])
    apps = sorted(set(services) - {'migration-runner'})
    assert len(apps) == 10
    checkout = str(project).replace('\\', '/').lower()
    plan = {'services': [{'repository': 'lotus-core', 'project': 'core', 'service': service} for service in services],
            'targetScope': {'projects': {'core': checkout}, 'sources': {'lotus-core': revision}}}
    evaluated = {'name': 'core', 'services': {service: {'build': {'context': str(project), 'dockerfile': 'Dockerfile'}} for service in services}}
    if case == 'restart-policy':
        evaluated['services']['migration-runner']['restart'] = 'always'
    plan['composeConfigDigest'] = digest(evaluated)
    plan_path = tmp_path / 'plan.json'
    plan_path.write_text(json.dumps(plan), encoding='utf-8')
    model_path = tmp_path / 'model.json'
    model_path.write_text(json.dumps(evaluated), encoding='utf-8')
    book = tmp_path / 'lotus-platform/output/canonical-runtime/reservations.v1.json'
    book.parent.mkdir(parents=True)
    book.write_text('{}', encoding='utf-8')
    lock = book.parent / 'operation.lock'
    log = tmp_path / 'calls.txt'
    command = f"""
$ErrorActionPreference='Stop'
$global:poll=0
function global:Assert-Fenced {{
  $contended=$false
  try {{ $probe=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); $probe.Dispose() }} catch [IO.IOException] {{ $contended=$true }}
  if (-not $contended) {{ throw 'IO_OUTSIDE_OPERATION_FENCE' }}
}}
function global:python {{
  if ($args[0] -like '*canonical_refresh_inputs.py') {{ & '{sys.executable}' @args; return }}
  Assert-Fenced
  $action=$args[1]; Add-Content -LiteralPath '{log}' -Value "lease:$action"
  $global:LASTEXITCODE=0
  $plan=Get-Content -LiteralPath '{plan_path}' -Raw | ConvertFrom-Json
  if ($action -eq 'begin-refresh') {{
    $resources=@($plan.services | ForEach-Object {{ @{{id=if ($_.service -eq 'migration-runner') {{ '{'a' * 64}' }} else {{ $_.service }};project='core';service=$_.service}} }})
    if ('{case}' -eq 'acquired-two') {{ $resources+=@{{id='{'e' * 64}';project='core';service='migration-runner'}} }}
    if ('{case}' -eq 'acquired-none') {{ $resources=@($resources | Where-Object {{ $_.service -ne 'migration-runner' }}) }}
    if ('{case}' -eq 'acquired-malformed-id') {{ ($resources | Where-Object {{ $_.service -eq 'migration-runner' }}).id='short-id' }}
    $bindings=@($resources | ForEach-Object {{ @{{id=$_.id;ports=@()}} }})
    return (@{{operation=@{{token='reviewed-token';refresh=@{{plan=$plan;originalResources=$resources}}}};bindings=$bindings;scope=@{{}}}} | ConvertTo-Json -Depth 12 -Compress)
  }}
  if ($action -eq 'prepare-refresh') {{
    $refsPath=$args[[Array]::IndexOf($args,'--prepared-images')+1]
    $refs=@(Get-Content -LiteralPath $refsPath -Raw | ConvertFrom-Json)
    if ($refs.Count -ne 11) {{ throw 'INCOMPLETE_PREPARE' }}
    foreach ($ref in $refs) {{ if ($ref.reference -ne "lotus-reserved-refresh:reviewed-token-$($ref.service)") {{ throw 'UNBOUNDED_PREPARE' }} }}
    $images=@($plan.services | ForEach-Object {{ @{{service=$_.service;project='core';repository='lotus-core';checkout='{checkout}';sourceRevision='{revision}';imageId='sha256:{'c' * 64}'}} }})
    if ('{case}' -eq 'prepare-missing') {{ $images=@($images | Where-Object {{ $_.service -ne 'migration-runner' }}) }}
    if ('{case}' -eq 'prepare-duplicate') {{ $images+=@($images | Where-Object {{ $_.service -eq 'migration-runner' }}) }}
    return (@{{operation=@{{refresh=@{{preparedImages=$images}}}}}} | ConvertTo-Json -Depth 12 -Compress)
  }}
  if ($action -eq 'finish-refresh') {{ Add-Content -LiteralPath '{log}' -Value ('outcome:'+$args[[Array]::IndexOf($args,'--outcome')+1]) }}
  return '{{}}'
}}
function global:MigrationFakeDocker {{
  Assert-Fenced
  $global:LASTEXITCODE=0
  Add-Content -LiteralPath '{log}' -Value ('docker:'+($args -join ' '))
  if ($args -contains 'config') {{ return Get-Content -LiteralPath '{model_path}' -Raw }}
  if ($args -contains 'build' -or $args -contains 'up') {{ return }}
  if ($args -contains 'ps') {{
    if ($args[-1] -eq 'migration-runner') {{
      if ($args -notcontains '--all') {{ throw 'COMPLETED_CONTAINERS_OMITTED' }}
      $global:poll++
      if ('{case}' -eq 'missing') {{ return '[]' }}
      if ('{case}' -eq 'malformed') {{ return 'not-json' }}
      $state=if ('{case}' -eq 'timeout' -or ('{case}' -in @('running-success','container-drift') -and $global:poll -eq 1)) {{ 'running' }} elseif ('{case}' -eq 'created-success' -and $global:poll -eq 1) {{ 'created' }} else {{ 'exited' }}
      $global:currentState=$state
      $id=if ('{case}' -eq 'container-drift' -and $global:poll -gt 1) {{ '{'d' * 64}' }} else {{ '{'b' * 64}' }}
      $staleId='{'e' * 64}'; $duplicateId='{'f' * 64}'
      # Compose truncates JSON IDs to 12 characters unless explicitly asked for full IDs.
      if ($args -notcontains '--no-trunc' -or '{case}' -eq 'truncated-id') {{
        $id=$id.Substring(0,12); $staleId=$staleId.Substring(0,12); $duplicateId=$duplicateId.Substring(0,12)
      }}
      $row=@{{Service='migration-runner';State=$state;ID=$id;Name='core-migration-runner-run-realservice'}}
      $stale=@{{Service='migration-runner';State='exited';ID=$staleId;Name='core-migration-runner-1'}}
      if ('{case}' -in @('readiness-only-oneoff-before','stale-missing-oneoff','stale-identity-drift')) {{ return ConvertTo-Json -InputObject @($stale,$row) -Compress }}
      if ('{case}' -eq 'readiness-only-oneoff-after') {{ return ConvertTo-Json -InputObject @($row,$stale) -Compress }}
      if ('{case}' -eq 'only-oneoff') {{ return ConvertTo-Json -InputObject @($stale) -Compress }}
      if ('{case}' -eq 'duplicate-real') {{ return ConvertTo-Json -InputObject @($row,@{{Service='migration-runner';State=$state;ID=$duplicateId}}) -Compress }}
      if ('{case}' -eq 'duplicate') {{ return ConvertTo-Json -InputObject @($row,$row) -Compress }}
      return $row | ConvertTo-Json -Compress
    }}
    if ($args -contains '--all') {{ throw 'DAEMON_QUERY_INCLUDES_STOPPED_ONEOFF' }}
    return ConvertTo-Json -InputObject @({','.join("@{Service='" + app + "';State='running';Health='healthy'}" for app in apps)}) -Compress
  }}
  if ($args[0] -eq 'inspect') {{
    if ($args[-1] -eq '{'a' * 64}') {{
      $original=@{{Id=$args[-1];Config=@{{Labels=@{{'com.docker.compose.project'='core';'com.docker.compose.service'='migration-runner';'com.docker.compose.oneoff'='False'}}}}}}
      switch ('{case}') {{
        'acquired-only-run' {{ $original.Config.Labels.'com.docker.compose.oneoff'='True' }}
        'acquired-missing-oneoff' {{ $original.Config.Labels.Remove('com.docker.compose.oneoff') }}
        'acquired-malformed-oneoff' {{ $original.Config.Labels.'com.docker.compose.oneoff'='unknown' }}
        'acquired-foreign-project' {{ $original.Config.Labels.'com.docker.compose.project'='foreign' }}
        'acquired-foreign-service' {{ $original.Config.Labels.'com.docker.compose.service'='foreign' }}
        'acquired-wrong-id' {{ $original.Id='{'d' * 64}' }}
        'acquired-inspect-failure' {{ $global:LASTEXITCODE=23; return }}
        'acquired-inspect-duplicate' {{ return ConvertTo-Json -InputObject @($original,$original) -Depth 12 -Compress }}
        'acquired-inspect-malformed' {{ return 'not-json' }}
      }}
      return ConvertTo-Json -InputObject @($original) -Depth 12 -Compress
    }}
    if ('{case}' -eq 'inspect-failure') {{ $global:LASTEXITCODE=23; return }}
    if ('{case}' -eq 'inspect-malformed') {{ return 'not-json' }}
    $container=@{{Id=$args[-1];Image='sha256:{'c' * 64}';RestartCount=0;Config=@{{Labels=@{{
      'com.docker.compose.project'='core';'com.docker.compose.service'='migration-runner';'com.docker.compose.oneoff'='False';
      'org.opencontainers.image.revision'='{revision}';'org.opencontainers.image.source'='lotus-core';'com.lotus.repository.checkout'='{checkout}'
    }}}};State=@{{Status=$global:currentState;ExitCode=0;OOMKilled=$false;Running=($global:currentState -eq 'running');Error=''}}}}
    if ($args[-1] -eq '{'e' * 64}') {{
      $container.Config.Labels.'com.docker.compose.oneoff'='True'
      $container.Image='sha256:{'d' * 64}'
      $container.Config.Labels.'org.opencontainers.image.revision'='{'d' * 40}'
      $container.State.ExitCode=17; $container.State.OOMKilled=$true; $container.RestartCount=2
      if ('{case}' -eq 'stale-missing-oneoff') {{ $container.Config.Labels.Remove('com.docker.compose.oneoff') }}
      if ('{case}' -eq 'stale-identity-drift') {{ $container.Config.Labels.'com.docker.compose.project'='foreign' }}
    }}
    switch ('{case}') {{
      'nonzero' {{ $container.State.ExitCode=17 }}
      'oom' {{ $container.State.OOMKilled=$true }}
      'restart' {{ $container.RestartCount=1 }}
      'project-drift' {{ $container.Config.Labels.'com.docker.compose.project'='foreign' }}
      'image-drift' {{ $container.Image='sha256:{'d' * 64}' }}
      'source-drift' {{ $container.Config.Labels.'org.opencontainers.image.revision'='{'d' * 40}' }}
      'missing-oneoff' {{ $container.Config.Labels.Remove('com.docker.compose.oneoff') }}
      'malformed-oneoff' {{ $container.Config.Labels.'com.docker.compose.oneoff'='unknown' }}
      'boolean-oneoff' {{ $container.Config.Labels.'com.docker.compose.oneoff'=$false }}
      'case-oneoff' {{ $container.Config.Labels.'com.docker.compose.oneoff'='false' }}
    }}
    if ('{case}' -eq 'inspect-duplicate') {{ return ConvertTo-Json -InputObject @($container,$container) -Depth 12 -Compress }}
    return ConvertTo-Json -InputObject @($container) -Depth 12 -Compress
  }}
  throw 'UNEXPECTED_DOCKER_COMMAND'
}}
& '{ROOT / 'automation/Service-Refresh.ps1'}' -ProjectPath '{project}' -ProjectsRoot '{tmp_path}' `
  -Services @({','.join(repr(service) for service in services)}) -DockerCommand MigrationFakeDocker `
  -HealthTimeoutSeconds {3 if case in {'running-success', 'created-success', 'container-drift'} else 0} -HealthPollIntervalSeconds 1 `
  -RuntimeHolder owner -RefreshPlan '{plan_path}' -RefreshPlanDigest sha256:reviewed
"""
    shell = shutil.which('pwsh') or shutil.which('powershell')
    assert shell
    result = subprocess.run([shell, '-NoProfile', '-Command', command], text=True, capture_output=True, timeout=30)
    calls = log.read_text(encoding='utf-8-sig').splitlines()
    assert 'IO_OUTSIDE_OPERATION_FENCE' not in result.stderr
    up = [call for call in calls if ' up ' in call]
    build = [call for call in calls if ' build ' in call]
    if case.startswith('acquired-'):
        assert result.returncode == 1, result.stdout + result.stderr
        expected = {
            'acquired-two': 'exactly one acquired service container before build',
            'acquired-none': 'exactly one acquired service container before build',
            'acquired-only-run': 'must be the actual Compose service before build',
            'acquired-malformed-id': 'Missing or malformed one-shot container identity',
            'acquired-missing-oneoff': 'Missing or malformed Compose one-off metadata',
            'acquired-malformed-oneoff': 'Missing or malformed Compose one-off metadata',
            'acquired-foreign-project': 'project/service/container identity mismatch',
            'acquired-foreign-service': 'project/service/container identity mismatch',
            'acquired-wrong-id': 'project/service/container identity mismatch',
            'acquired-inspect-failure': 'container inspection failed',
            'acquired-inspect-duplicate': 'Ambiguous one-shot container inspection',
            'acquired-inspect-malformed': 'json',
        }[case]
        assert expected.lower() in result.stderr.lower(), result.stderr
        assert not build and not up, calls
        assert calls[-1] == 'outcome:failure'
        assert 'lease:prepare-refresh' not in calls
        return
    if case == 'restart-policy':
        assert result.returncode == 1, result.stdout + result.stderr
        assert 'must not automatically restart' in result.stderr
        assert not up and not build
        assert calls[-1] == 'outcome:failure'
        return
    assert len(build) == 1 and set(build[0].split(' build ')[1].split()) == set(services)
    if case in {'prepare-missing', 'prepare-duplicate'}:
        assert result.returncode == 1, result.stdout + result.stderr
        assert 'Missing or ambiguous prepared one-shot image' in result.stderr
        assert not up
        assert calls[-1] == 'outcome:failure'
        return
    assert calls.index(build[0]) < calls.index('lease:prepare-refresh') < calls.index(up[0])
    assert up[0].endswith('up -d --no-deps --no-build --pull never --force-recreate migration-runner')
    success = case in {'success', 'running-success', 'created-success', 'readiness-only-oneoff-before', 'readiness-only-oneoff-after'}
    observations = [call for call in calls if ' ps ' in call]
    assert observations and all(' --no-trunc --format json ' in call for call in observations), calls
    assert all(' ps --all ' in call for call in observations if call.endswith('migration-runner')), calls
    if case == 'truncated-id':
        assert 'Missing or malformed one-shot container identity' in result.stderr
        assert not any(call.startswith('docker:inspect --type container ' + 'b' * 12) for call in calls)
    assert result.returncode == (0 if success else 1), result.stdout + result.stderr
    assert calls[-1] == ('outcome:success' if success else 'outcome:failure')
    assert len(up) == (2 if success else 1), calls
    if success:
        assert up[1].endswith('up -d --no-deps --no-build --pull never ' + ' '.join(apps))
        inspections = [call for call in calls if call.startswith('docker:inspect ')]
        assert inspections and calls.index(inspections[-1]) < calls.index(up[1])
        assert len(inspections) == (2 if case == 'success' else 3)
        assert calls.index(inspections[0]) < calls.index(build[0])
    assert not any(name in ' '.join(up) for name in ('demo_data_loader', 'kafka-topic-creator', 'postgres', 'zookeeper'))
    assert book.read_text(encoding='utf-8') == '{}'


@pytest.mark.parametrize('case', ['missing', 'foreign', 'digest', 'foreign-context', 'port-drift', 'build-failure', 'image-source', 'up-failure', 'readiness', 'success',
                                'external-compose', 'untracked-compose', 'dirty-compose', 'env-compose', 'preview', 'preview-digest', 'preview-context',
                                'tracked-compose', 'ignored-compose', 'reparse-compose', 'mismatched-project', 'preview-mismatched-project',
                                'ancestor-context', 'ancestor-dockerfile', 'preview-ancestor-context',
                                'ignored-context', 'preview-ignored-context', 'shell-config', 'env-config', 'preview-env-config', 'preview-workers'])
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
    if case == 'preview-workers':
        # Evaluated Compose omits ports on workers; retain a second explicit-empty control.
        for worker in ('compute-worker', 'lineage-worker'):
            plan['services'].append({'repository': 'lotus-gateway', 'project': 'gateway', 'service': worker})
            evaluated['services'][worker] = {'build': dict(evaluated['services']['lotus-gateway']['build'])}
        evaluated['services']['lineage-worker']['ports'] = []
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
    $resources=@(@{{id='old';project='gateway';service='lotus-gateway'}})
    $bindings=@(@{{id='old';ports=@(8111)}})
    if ($global:case -eq 'preview-workers') {{
      foreach ($worker in @('compute-worker','lineage-worker')) {{
        $resources+=@{{id=$worker;project='gateway';service=$worker}}
        $bindings+=@{{id=$worker;ports=@()}}
      }}
    }}
    return (@{{operation=@{{token='reviewed-token'; refresh=@{{plan=$plan;originalResources=$resources}}}}; bindings=$bindings; scope=@{{}}}} | ConvertTo-Json -Depth 12 -Compress)
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
  -Services {"@('lotus-gateway','compute-worker','lineage-worker')" if case == 'preview-workers' else 'lotus-gateway'} -DockerCommand ReservedFakeDocker -HealthTimeoutSeconds 0 `
  {'' if case == 'missing' else f"-RuntimeHolder owner -RefreshPlan '{plan_path}' -RefreshPlanDigest sha256:reviewed"} `
  {f"-ComposeFiles '{extra}'" if case in {'external-compose', 'untracked-compose', 'tracked-compose', 'ignored-compose', 'reparse-compose'} else ''} {'-DryRun' if case.startswith('preview') else ''}
"""
    shell = (shutil.which('powershell') if os.name == 'nt' and case == 'preview-workers' else None) or shutil.which('pwsh') or shutil.which('powershell')
    assert shell
    result = subprocess.run([shell, '-NoProfile', '-Command', command], text=True, capture_output=True, timeout=30)
    calls = log.read_text(encoding='utf-8-sig').splitlines() if log.exists() else []
    assert 'IO_OUTSIDE_OPERATION_FENCE' not in result.stderr
    docker = [row for row in calls if row.startswith('docker:') and ' config ' not in row]
    if case.startswith('preview'):
        assert result.returncode == (0 if case in {'preview', 'preview-ignored-context', 'preview-workers'} else 1), result.stdout + result.stderr
        assert docker == []
        assert 'lease:begin-refresh' not in calls and 'lease:finish-refresh' not in calls
        assert book.read_text(encoding='utf-8') == '{}'
        if case == 'preview':
            assert 'up -d --no-deps --no-build --pull never' in result.stdout
            assert 'up -d --build' not in result.stdout
        if case == 'preview-workers':
            assert 'up -d --no-deps --no-build --pull never compute-worker lineage-worker lotus-gateway' in result.stdout
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


@pytest.mark.parametrize('shell_name', ['powershell', 'pwsh'])
def test_reserved_compose_port_shapes_on_native_shells(tmp_path, shell_name):
    shell = shutil.which(shell_name)
    if shell is None:
        pytest.skip(f'{shell_name} is not available on this platform')
    (tmp_path / 'Dockerfile').write_text('FROM scratch', encoding='utf-8')
    command = f"""
$ErrorActionPreference='Stop'
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile('{ROOT / 'automation/Service-Refresh.ps1'}',[ref]$tokens,[ref]$errors)
if ($errors.Count) {{ throw 'Shipped adapter failed to parse' }}
foreach ($name in @('Assert-ReviewedRepositoryPath','Assert-ReservedComposeInputs')) {{
  $node=$ast.Find({{param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name}},$true)
  Invoke-Expression $node.Extent.Text
}}
function ControlledConfig {{ $global:LASTEXITCODE=0; return $global:model | ConvertTo-Json -Depth 10 -Compress }}
$planned=@(@{{project='performance';service='api'}},@{{project='performance';service='worker'}})
$cases=@('omitted','empty','range','malformed','missing-publication','null-entry','api-binding-drift','worker-binding-drift')
foreach ($case in $cases) {{
  $global:model=@{{name='performance';services=@{{
    api=@{{build=@{{context='{tmp_path}';dockerfile='Dockerfile'}};ports=@(@{{published='8002'}})}}
    worker=@{{build=@{{context='{tmp_path}';dockerfile='Dockerfile'}}}}
  }}}}
  $bindings=@(@{{id='api-id';ports=@(8002)}},@{{id='worker-id';ports=@()}})
  switch ($case) {{
    'empty' {{ $global:model.services.worker.ports=@() }}
    'range' {{ $global:model.services.worker.ports=@(@{{published='8002-8004'}}) }}
    'malformed' {{ $global:model.services.worker.ports=@(@{{published='invalid'}}) }}
    'missing-publication' {{ $global:model.services.worker.ports=@(@{{target=8000}}) }}
    'null-entry' {{ $global:model.services.worker.ports=@($null) }}
    'api-binding-drift' {{ $bindings[0].ports=@(8003) }}
    'worker-binding-drift' {{ $bindings[1].ports=@(8004) }}
  }}
  $operation=@{{OriginalResources=@(@{{id='api-id';project='performance';service='api'}},@{{id='worker-id';project='performance';service='worker'}});Bindings=$bindings}}
  $failure=$null
  try {{ $actual=Assert-ReservedComposeInputs -Command ControlledConfig -Prefix @('compose') -Operation $operation -PlannedServices $planned -RepoPath '{tmp_path}' }}
  catch {{ $failure=$_.Exception.Message }}
  if ($case -in @('omitted','empty')) {{
    if ($failure) {{ throw "$case unexpectedly refused: $failure" }}
    if (($actual | ConvertFrom-Json).services.api.ports[0].published -ne '8002') {{ throw 'Evaluated model changed' }}
  }} else {{
    $expected=if ($case -like '*binding-drift') {{ 'publications differ from original bindings' }} else {{ 'requires bounded published ports' }}
    if (-not $failure -or $failure -notlike "*$expected*") {{ throw "$case did not refuse as expected: $failure" }}
  }}
  Write-Output "CONTROL_PASS:$case"
}}
"""
    result = subprocess.run([shell, '-NoProfile', '-Command', command], text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count('CONTROL_PASS:') == 8
