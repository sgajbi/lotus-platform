from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from automation.canonical_refresh_inputs import freeze, resolve_build_owners
from automation.canonical_runtime_lease import ReservationRefusal, digest


@pytest.mark.parametrize('case', ['committed-inputs',
                                 'digest-build-arg', 'digest-command', 'digest-mount', 'digest-env',
                                 'missing-dockerfile', 'symlink', 'submodule', 'unresolved-env', 'unresolved-arg'])
def test_frozen_model_uses_reviewed_configuration_and_committed_blobs(tmp_path: Path, case: str) -> None:
    repo = tmp_path / 'repository'
    repo.mkdir()
    def git(*args: str) -> str:
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
    git('init')
    (repo / 'Dockerfile').write_bytes(b'FROM scratch\nCOPY . /source\n')
    (repo / 'payload').write_bytes(b'reviewed\x00bytes\r\n')
    (repo / '.gitignore').write_text('ignored\n', encoding='utf-8')
    (repo / '.gitattributes').write_text('payload export-ignore\n', encoding='utf-8')
    git('add', '.')
    git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', '-c', 'commit.gpgsign=false',
        'commit', '-m', 'reviewed')
    revision = git('rev-parse', 'HEAD')
    if case in {'symlink', 'submodule'}:
        mode, object_id = ('120000', git('rev-parse', 'HEAD:payload')) if case == 'symlink' else ('160000', revision)
        git('update-index', '--add', '--cacheinfo', f'{mode},{object_id},redirect')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test', '-c', 'commit.gpgsign=false',
            'commit', '-m', 'unsupported entry')
        revision = git('rev-parse', 'HEAD')
    (repo / 'ignored').write_text('unreviewed ignored input', encoding='utf-8')
    (repo / 'untracked').write_text('unreviewed untracked input', encoding='utf-8')
    (repo / 'payload').write_text('unreviewed working content', encoding='utf-8')
    config = {'name': 'reviewed-project', 'services': {'selected': {
        'build': {'context': str(repo), 'dockerfile': 'Dockerfile', 'args': {'APP_GIT_COMMIT_SHA': revision, 'APP_GIT_BRANCH': 'main'}},
        'command': ['sh', '-c', 'echo $$TOKEN $$$$literal'],
        'environment': {'TOKEN': '$$secret'},
        'volumes': [{'type': 'bind', 'source': str(repo / 'payload'), 'target': '/data'}],
        'labels': {'com.docker.compose.project.working_dir': str(repo)},
    }}}
    reviewed_digest = digest(config)
    actual = copy.deepcopy(config)
    service = actual['services']['selected']
    if case == 'digest-build-arg': service['build']['args']['APP_GIT_BRANCH'] = 'unreviewed'
    elif case == 'digest-command': service['command'][2] = 'unreviewed command'
    elif case == 'digest-mount': service['volumes'][0]['source'] = str(tmp_path / 'foreign')
    elif case == 'digest-env': service['environment']['TOKEN'] = 'unreviewed secret'
    elif case == 'missing-dockerfile': service['build']['dockerfile'] = 'untracked'
    elif case == 'unresolved-env': service['environment']['TOKEN'] = None
    elif case == 'unresolved-arg': service['build']['args']['APP_GIT_BRANCH'] = None
    if case in {'missing-dockerfile', 'unresolved-env', 'unresolved-arg'}: reviewed_digest = digest(actual)
    output = tmp_path / 'snapshot'
    output.mkdir()
    if case.startswith('digest-') or case in {'missing-dockerfile', 'symlink', 'submodule', 'unresolved-env', 'unresolved-arg'}:
        with pytest.raises(ReservationRefusal):
            freeze(repo, revision, actual, reviewed_digest, output, ['selected'])
        assert not (output / 'compose.json').exists()
        if case.startswith('digest-'):
            assert not (output / 'source').exists()
    else:
        model_path = freeze(repo, revision, actual, reviewed_digest, output, ['selected'])
        frozen = json.loads(model_path.read_text(encoding='utf-8'))
        built = frozen['services']['selected']
        context = Path(built['build']['context'])
        assert context != repo
        assert (context / 'payload').read_bytes() == b'reviewed\x00bytes\r\n'
        assert not (context / 'ignored').exists() and not (context / 'untracked').exists()
        assert Path(built['build']['dockerfile']).read_bytes() == b'FROM scratch\nCOPY . /source\n'
        assert built['build']['args'] == service['build']['args']
        for field in ('command', 'environment', 'volumes', 'labels'):
            assert built[field] == service[field]


@pytest.mark.parametrize('case,expected', [
    ('valid', None), ('direct', None), ('zero', 'exactly one build owner'),
    ('ambiguous', 'exactly one build owner'), ('mismatch', 'exactly one build owner'),
    ('missing-image', 'explicit shared image'), ('inline', 'local owned context'),
    ('additional', 'local owned context'), ('missing-context', 'local owned context'),
    ('tags', 'additional image tags'),
])
def test_shared_image_owner_resolution_is_exact_and_preserves_single_writer(case, expected):
    model = {'services': {'api': {'image': 'app:local'}, 'worker': {'image': 'app:local'},
                          'migration': {'image': 'app:local', 'build': {'context': '/owned'}}}}
    if case == 'zero': del model['services']['migration']['build']
    if case == 'ambiguous': model['services']['other'] = copy.deepcopy(model['services']['migration'])
    if case == 'mismatch': model['services']['migration']['image'] = 'app:other'
    if case == 'missing-image': del model['services']['api']['image']
    if case == 'inline': model['services']['migration']['build']['dockerfile_inline'] = 'FROM scratch'
    if case == 'additional': model['services']['migration']['build']['additional_contexts'] = {'foreign': '/foreign'}
    if case == 'missing-context': del model['services']['migration']['build']['context']
    if case == 'tags': model['services']['migration']['build']['tags'] = ['app:local']
    if case == 'direct':
        model['services']['api']['build'] = {'context': '/owned'}
        model['services']['api']['image'] = 'api:own'
    original = copy.deepcopy(model)
    if expected:
        with pytest.raises(ReservationRefusal, match=expected):
            resolve_build_owners(model, ['api', 'worker'])
    else:
        assert resolve_build_owners(model, ['api', 'worker']) == {
            'api': 'api' if case == 'direct' else 'migration', 'worker': 'migration'}
    assert model == original


@pytest.mark.parametrize('shared', [False, True], ids=['direct', 'shared'])
@pytest.mark.parametrize('field,value', [
    ('secrets', ['SYNTHETIC_SECRET_REFERENCE']),
    ('secrets', [{'source': 'SYNTHETIC_SECRET_REFERENCE', 'target': 'build-only'}]),
    ('ssh', ['default=SYNTHETIC_SSH_SOCKET']),
])
def test_auxiliary_build_authority_refuses_before_export(tmp_path, monkeypatch, shared, field, value):
    owner = 'migration' if shared else 'api'
    model = {'services': {'api': {'image': 'app:local'}}}
    model['services'].setdefault(owner, {'image': 'app:local'})['build'] = {
        'context': str(tmp_path), field: value}
    model['secrets'] = {'SYNTHETIC_SECRET_REFERENCE': {'file': 'SYNTHETIC_HOST_PATH'}}
    original = copy.deepcopy(model)
    def forbidden_export(*_):
        pytest.fail('UNFROZEN_AUXILIARY_EXPORT_REACHED')
    monkeypatch.setattr('automation.canonical_refresh_inputs.export_commit', forbidden_export)
    with pytest.raises(ReservationRefusal, match='Reserved build cannot use auxiliary secrets or SSH inputs') as error:
        freeze(tmp_path, 'a' * 40, model, digest(model), tmp_path, ['api'])
    assert str(error.value) == 'Reserved build cannot use auxiliary secrets or SSH inputs.'
    assert not (tmp_path / 'source').exists() and not (tmp_path / 'compose.json').exists()
    assert model == original


@pytest.mark.parametrize('shared', [False, True], ids=['direct', 'shared'])
@pytest.mark.parametrize('auxiliary', [{}, {'secrets': []}, {'ssh': []},
                                    {'secrets': None, 'ssh': None}, {'secrets': {}, 'ssh': {}}])
def test_build_owners_accept_absent_or_empty_auxiliary_inputs(shared, auxiliary):
    owner = 'migration' if shared else 'api'
    model = {'services': {'api': {'image': 'app:local'}}}
    model['services'].setdefault(owner, {'image': 'app:local'})['build'] = {
        'context': '/owned', **auxiliary}
    model['secrets'] = {'runtime-only': {'external': True}}
    original = copy.deepcopy(model)
    assert resolve_build_owners(model, ['api']) == {'api': owner}
    assert model == original
