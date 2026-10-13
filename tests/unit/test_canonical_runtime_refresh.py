from __future__ import annotations

import copy
import json
from argparse import Namespace
from datetime import datetime, timedelta, timezone

import pytest

from automation import canonical_runtime_lease as lease
from automation import canonical_runtime_refresh as refresh
from automation.canonical_runtime_reservation import transact

NOW = datetime(2026, 10, 13, tzinfo=timezone.utc)
HOLDER = 'reviewed-owner'
SCOPE = {'projects': {'core': 'c:/projects/lotus-core', 'gateway': 'c:/projects/lotus-gateway'},
         'ports': [8111, 8202], 'sources': {'lotus-core': 'a' * 40, 'lotus-gateway': 'b' * 40}}
BINDINGS = [
    {'kind': 'container', 'id': 'core-old', 'project': 'core', 'checkout': SCOPE['projects']['core'], 'ports': [8202]},
    {'kind': 'container', 'id': 'gateway-old', 'project': 'gateway', 'checkout': SCOPE['projects']['gateway'], 'ports': [8111]},
]
RESOURCES = [
    {'id': binding['id'], 'project': binding['project'], 'service': binding['project'],
     'checkout': binding['checkout'], 'imageId': 'sha256:' + letter * 64,
     'sourceRevision': SCOPE['sources'][repo], 'repository': repo}
    for binding, repo, letter in zip(BINDINGS, ['lotus-core', 'lotus-gateway'], ['a', 'b'])
]


def fixture(source_only=False):
    book = lease.empty_book()
    receipt = {'holder': HOLDER, 'operator': 'operator', 'sourceReceipt': 'initial-admission',
               'scopeDigest': lease.digest(SCOPE), 'bindingsDigest': lease.digest(BINDINGS)}
    lease.acquire(book, holder=HOLDER, purpose='#901 bounded refresh', expires=(NOW + timedelta(hours=2)).isoformat(),
                  scope=copy.deepcopy(SCOPE), bindings=copy.deepcopy(BINDINGS), now=NOW, reservation_id='original', receipt=receipt)
    target = copy.deepcopy(SCOPE)
    target['sources']['lotus-core'] = 'c' * 40
    plan = {'schemaVersion': 'lotus.canonical-runtime.refresh.v1', 'reservationId': 'original', 'holder': HOLDER,
            'operator': 'operator', 'sourceReceipt': 'reviewed-target', 'originalScopeDigest': lease.digest(SCOPE),
            'originalBindingsDigest': lease.digest(BINDINGS), 'targetScope': target,
            'repositoryChanges': {'lotus-core': {'from': 'a' * 40, 'to': 'c' * 40,
                                               'disposition': 'source-only' if source_only else 'service-refresh'}},
            'services': [] if source_only else [{'repository': 'lotus-core', 'project': 'core', 'service': 'core'}]}
    if not source_only:
        plan['composeConfigDigest'] = 'sha256:' + 'd' * 64
    common = {'holder': HOLDER, 'scope': target, 'bindings': copy.deepcopy(BINDINGS),
              'resources': copy.deepcopy(RESOURCES), 'now': NOW}
    return book, plan, common


def begin(book, plan, common):
    return refresh.begin(book, **common, plan=plan, plan_digest=lease.digest(plan), token='refresh-token')


def replacement(plan):
    images = [{'project': 'core', 'service': 'core', 'repository': 'lotus-core', 'checkout': SCOPE['projects']['core'],
               'sourceRevision': plan['targetScope']['sources']['lotus-core'], 'imageId': 'sha256:' + 'c' * 64}]
    bindings, resources = copy.deepcopy(BINDINGS), copy.deepcopy(RESOURCES)
    bindings[0]['id'] = resources[0]['id'] = 'core-new'
    resources[0].update(images[0])
    return images, bindings, resources


def test_bounded_build_refresh_preserves_reservation_expiry_and_untouched_then_strict_proof_and_teardown():
    book, plan, common = fixture()
    original = copy.deepcopy(book['reservations'][0])
    begin(book, plan, common)
    images, bindings, resources = replacement(plan)
    refresh.prepare(book, **common, token='refresh-token', images=images)
    record = refresh.finish(book, **{**common, 'bindings': bindings, 'resources': resources},
                            token='refresh-token', outcome='success')
    for field in ('id', 'holder', 'purpose', 'startUtc', 'expiryUtc', 'teardownOwner'):
        assert record[field] == original[field]
    assert record['bindings'][1] == original['bindings'][1]
    assert record['events'][-1]['runtimeImages'][1] == RESOURCES[1]
    proof = {key: value for key, value in {**common, 'bindings': bindings}.items() if key != 'resources'}
    lease.preflight(book, **proof)
    lease.begin(book, **proof, action='teardown', token='teardown')
    lease.finish(book, **{**proof, 'bindings': []}, token='teardown', outcome='success')
    assert lease.current(book) is None


def test_source_only_keeps_images_honestly_distinct_from_new_host_sources():
    book, plan, common = fixture(source_only=True)
    begin(book, plan, common)
    record = refresh.finish(book, **common, token='refresh-token', outcome='success')
    assert record['scope']['sources']['lotus-core'] == 'c' * 40
    assert record['bindings'] == BINDINGS
    assert record['events'][-1]['runtimeImages'][0]['sourceRevision'] == 'a' * 40
    lease.preflight(book, **{k: v for k, v in common.items() if k != 'resources'})


@pytest.mark.parametrize('case', ['holder', 'expired', 'scope-digest', 'binding-digest', 'reservation', 'target',
                                 'ports', 'projects', 'mode', 'from', 'allowlist', 'source-only-service', 'concurrent',
                                 'missing-compose-digest', 'malformed-compose-digest'])
def test_adverse_begin_is_atomic_and_does_not_regrant(tmp_path, case):
    book, plan, common = fixture()
    if case == 'holder': common['holder'] = 'foreign'
    elif case == 'expired': common['now'] += timedelta(hours=3)
    elif case == 'scope-digest': plan['originalScopeDigest'] = 'wrong'
    elif case == 'binding-digest': plan['originalBindingsDigest'] = 'wrong'
    elif case == 'reservation': plan['reservationId'] = 'other'
    elif case == 'target': common['scope'] = copy.deepcopy(SCOPE)
    elif case == 'ports': plan['targetScope']['ports'] = [8111]
    elif case == 'projects': plan['targetScope']['projects']['core'] = 'c:/foreign'
    elif case == 'mode': plan['targetScope']['sources']['other'] = 'd' * 40
    elif case == 'from': plan['repositoryChanges']['lotus-core']['from'] = 'd' * 40
    elif case == 'allowlist': plan['services'][0]['project'] = 'foreign'
    elif case == 'source-only-service': plan['repositoryChanges']['lotus-core']['disposition'] = 'source-only'
    elif case == 'concurrent': begin(book, plan, common)
    elif case == 'missing-compose-digest': plan.pop('composeConfigDigest')
    elif case == 'malformed-compose-digest': plan['composeConfigDigest'] = 'unreviewed'
    path = tmp_path / 'book.json'
    path.write_text(json.dumps(book), encoding='utf-8')
    original = path.read_bytes()
    with pytest.raises(lease.ReservationRefusal):
        transact(path, lambda value: begin(value, plan, common), write=True)
    assert path.read_bytes() == original


def test_review_digest_and_unprepared_image_replacement_refuse():
    book, plan, common = fixture()
    with pytest.raises(lease.ReservationRefusal, match='digest'):
        refresh.begin(book, **common, plan=plan, plan_digest='wrong', token='refresh-token')
    begin(book, plan, common)
    _, bindings, resources = replacement(plan)
    with pytest.raises(lease.ReservationRefusal, match='preparation'):
        refresh.finish(book, **{**common, 'bindings': bindings, 'resources': resources}, token='refresh-token', outcome='success')


@pytest.mark.parametrize('field,value', [('sourceRevision', 'd' * 40), ('repository', 'lotus-gateway'),
                                       ('checkout', 'c:/foreign'), ('imageId', 'mutable-tag')])
def test_wrong_prepared_image_preserves_original_and_pending(field, value):
    book, plan, common = fixture()
    begin(book, plan, common)
    images, _, _ = replacement(plan)
    images[0][field] = value
    original = copy.deepcopy(book)
    with pytest.raises(lease.ReservationRefusal):
        refresh.prepare(book, **common, token='refresh-token', images=images)
    assert book == original


@pytest.mark.parametrize('case', ['untouched-id', 'untouched-image', 'untouched-ports', 'replacement-image', 'extra-host'])
def test_wrong_finish_cannot_publish_success(case):
    book, plan, common = fixture()
    begin(book, plan, common)
    images, bindings, resources = replacement(plan)
    refresh.prepare(book, **common, token='refresh-token', images=images)
    if case == 'untouched-id': bindings[1]['id'] = resources[1]['id'] = 'gateway-replaced'
    elif case == 'untouched-image': resources[1]['imageId'] = 'sha256:' + 'e' * 64
    elif case == 'untouched-ports': bindings[1]['ports'] = []
    elif case == 'replacement-image': resources[0]['imageId'] = 'sha256:' + 'e' * 64
    elif case == 'extra-host': bindings.append({'kind': 'host-process', 'id': 'pid:birth', 'project': 'host-listener', 'checkout': '', 'ports': [8111]})
    bindings.sort(key=lambda item: (item['kind'], item['id']))
    original = copy.deepcopy(book)
    with pytest.raises(lease.ReservationRefusal):
        refresh.finish(book, **{**common, 'bindings': bindings, 'resources': resources}, token='refresh-token', outcome='success')
    assert book == original


def test_failure_pending_cannot_be_cleared_by_normal_finish_recover_or_proof():
    book, plan, common = fixture()
    begin(book, plan, common)
    refresh.finish(book, **common, token='refresh-token', outcome='failure')
    assert book['reservations'][0]['scope'] == SCOPE
    ordinary = {k: v for k, v in {**common, 'scope': SCOPE}.items() if k != 'resources'}
    for action, extra in [(lease.preflight, {}), (lease.finish, {'token': 'refresh-token', 'outcome': 'success'}),
                          (lease.recover, {'receipt': {}})]:
        with pytest.raises(lease.ReservationRefusal): action(book, **ordinary, **extra)
    assert book['reservations'][0]['operation'] is not None


@pytest.mark.parametrize('disposition', ['abort', 'complete'])
def test_reviewed_recovery_requires_exact_restored_or_completed_resources(disposition):
    book, plan, common = fixture()
    begin(book, plan, common)
    images, bindings, resources = replacement(plan)
    refresh.prepare(book, **common, token='refresh-token', images=images)
    observed = {**common, 'bindings': bindings, 'resources': resources} if disposition == 'complete' else {**common, 'scope': SCOPE}
    receipt = {'holder': HOLDER, 'operator': 'recovery-operator', 'sourceReceipt': 'reviewed-recovery',
               'scopeDigest': lease.digest(observed['scope']), 'bindingsDigest': lease.digest(observed['bindings']),
               'reservationId': 'original', 'refreshPlanDigest': lease.digest(plan), 'disposition': disposition}
    bad = {**receipt, 'refreshPlanDigest': 'wrong'}
    with pytest.raises(lease.ReservationRefusal): refresh.recover(book, **observed, receipt=bad)
    record = refresh.recover(book, **observed, receipt=receipt)
    assert record['operation'] is None
    assert record['scope'] == observed['scope']
    lease.validate_book(book)


def test_shipped_cli_durable_refresh_then_strict_proof_uses_observed_immutable_images(tmp_path, monkeypatch):
    from automation import canonical_runtime_reservation as cli

    book, plan, common = fixture()
    projects = {name: str(tmp_path / ('lotus-' + name)).replace('\\', '/').lower() for name in ('core', 'gateway')}
    for scope in (book['reservations'][0]['scope'], plan['targetScope']): scope['projects'] = projects
    for bindings in (book['reservations'][0]['bindings'], common['bindings']):
        for binding in bindings: binding['checkout'] = projects[binding['project']]
    for resource in common['resources']: resource['checkout'] = projects[resource['project']]
    book['reservations'][0]['scopeDigest'] = plan['originalScopeDigest'] = lease.digest(book['reservations'][0]['scope'])
    plan['originalBindingsDigest'] = lease.digest(book['reservations'][0]['bindings'])
    common['scope'] = plan['targetScope']
    monkeypatch.setattr(cli, '__file__', str(tmp_path / 'lotus-platform/automation/canonical_runtime_reservation.py'))
    class Clock:
        @staticmethod
        def now(_zone): return NOW
    monkeypatch.setattr(cli, 'datetime', Clock)
    monkeypatch.setattr(cli, 'scope_for', lambda *_args: common['scope'])
    monkeypatch.setattr(cli, 'observe', lambda _scope: common['bindings'])
    monkeypatch.setattr(cli, 'observe_refresh_resources', lambda *_args: common['resources'])
    monkeypatch.setattr(cli, 'command', lambda *_args: '')
    images = [{'project': 'core', 'service': 'core', 'repository': 'lotus-core', 'checkout': projects['core'],
               'sourceRevision': 'c' * 40, 'imageId': 'sha256:' + 'c' * 64}]
    monkeypatch.setattr(cli, 'observe_prepared_images', lambda _refs: images)
    plan_file, refs_file, book_file = (tmp_path / name for name in ('plan.json', 'refs.json', 'book.json'))
    for path, value in ((plan_file, plan), (refs_file, []), (book_file, book)):
        path.write_text(json.dumps(value), encoding='utf-8')
    args = Namespace(action='begin-refresh', projects_root=str(tmp_path), workbench_repo_path='', runtime_mode='full',
                     holder=HOLDER, handover_receipt=None, refresh_plan=str(plan_file), refresh_plan_digest=lease.digest(plan),
                     operation_token='', prepared_images=str(refs_file), outcome='success')
    def run(action, write=True):
        args.action = action
        return transact(book_file, lambda value: cli.execute(args, value), write=write)
    original = book_file.read_bytes()
    preview = run('preview-refresh', write=False)
    assert preview['operation']['refresh']['plan'] == plan
    assert book_file.read_bytes() == original
    args.refresh_plan_digest = 'stale'
    with pytest.raises(lease.ReservationRefusal, match='digest'):
        run('preview-refresh', write=False)
    assert book_file.read_bytes() == original
    args.refresh_plan_digest = lease.digest(plan)
    record = run('begin-refresh')
    args.operation_token = record['operation']['token']
    run('prepare-refresh')
    common['bindings'][0]['id'] = common['resources'][0]['id'] = 'core-new'
    common['resources'][0].update(images[0])
    record = run('finish-refresh')
    assert record['id'] == 'original' and record['operation'] is None
    assert run('preflight', write=False)['scope'] == plan['targetScope']
    lease.validate_book(json.loads(book_file.read_text(encoding='utf-8')))


def test_image_inspection_uses_actual_container_id_and_immutable_image_not_tag(monkeypatch):
    from automation import canonical_runtime_inventory as inventory
    calls = []
    container = {'Id': 'core-old', 'Image': 'sha256:' + 'a' * 64,
                 'Config': {'Labels': {'com.docker.compose.service': 'core'}}}
    def command(arguments):
        calls.append(arguments)
        if arguments[:2] == ['docker', 'inspect']: return json.dumps([container])
        assert arguments == ['docker', 'image', 'inspect', container['Image']]
        return json.dumps([{'Id': container['Image'], 'Config': {'Labels': {
            'org.opencontainers.image.revision': 'a' * 40, 'org.opencontainers.image.source': 'lotus-core',
            'com.lotus.repository.checkout': SCOPE['projects']['core']}}}])
    monkeypatch.setattr(inventory, 'command', command)
    monkeypatch.setattr(inventory, 'select_containers', lambda *_args: BINDINGS[:1])
    assert inventory.observe_refresh_resources(SCOPE, BINDINGS[:1]) == RESOURCES[:1]
    assert calls[0] == ['docker', 'inspect', 'core-old']
    container['Image'] = 'sha256:' + 'f' * 64
    monkeypatch.setattr(inventory, 'command', lambda args: json.dumps([container]) if args[1] == 'inspect' else json.dumps([{'Id': 'sha256:' + 'a' * 64}]))
    with pytest.raises(lease.ReservationRefusal, match='image observation'):
        inventory.observe_refresh_resources(SCOPE, BINDINGS[:1])
