from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from automation.canonical_refresh_inputs import freeze
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
