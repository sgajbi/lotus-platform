"""Freeze reviewed Compose configuration and export committed build inputs."""
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
from pathlib import Path

try:
    from automation.canonical_runtime_lease import ReservationRefusal, digest, require
except ModuleNotFoundError:
    from canonical_runtime_lease import ReservationRefusal, digest, require


def git(repo: Path, *arguments: str, data: bytes | None = None) -> bytes:
    return subprocess.run(['git', '-C', str(repo), *arguments], input=data,
                          capture_output=True, check=True).stdout


def export_commit(repo: Path, revision: str, destination: Path) -> None:
    """Read blobs, never the index, archive attributes or ignored working files."""
    require(git(repo, 'rev-parse', 'HEAD').decode().strip() == revision,
            'Build snapshot source differs from reviewed revision.')
    entries = []
    for record in git(repo, 'ls-tree', '-rz', '--full-tree', revision).split(b'\0'):
        if not record:
            continue
        metadata, name = record.split(b'\t', 1)
        mode, kind, object_id = metadata.split()
        require(mode in {b'100644', b'100755'} and kind == b'blob',
                'Committed build snapshot does not support symlinks or submodules.')
        relative = Path(os.fsdecode(name))
        require(not relative.is_absolute() and '..' not in relative.parts,
                'Invalid committed build path.')
        entries.append((relative, mode, object_id))
    # One batch preserves exact blob bytes, including executable script contents.
    blobs = git(repo, 'cat-file', '--batch', data=b''.join(row[2] + b'\n' for row in entries))
    offset = 0
    destination.mkdir()
    for relative, mode, expected_id in entries:
        end = blobs.index(b'\n', offset)
        object_id, kind, size = blobs[offset:end].split()
        require(object_id == expected_id and kind == b'blob', 'Committed blob identity changed.')
        count = int(size)
        content = blobs[end + 1:end + 1 + count]
        require(len(content) == count and blobs[end + 1 + count:end + 2 + count] == b'\n',
                'Incomplete committed build blob.')
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(0o755 if mode == b'100755' else 0o644)
        offset = end + count + 2
    require(offset == len(blobs), 'Unexpected committed build blob output.')


def resolve_build_owners(config: dict, services: list[str]) -> dict[str, str]:
    """Resolve construction separately from the reviewed replacement allowlist."""
    model = config.get('services')
    require(isinstance(model, dict) and bool(services), 'Explicit Compose services required.')
    owners = {}
    for name in services:
        service = model.get(name)
        require(isinstance(service, dict), 'Selected Compose service is missing.')
        if 'build' in service:
            owner = name
        else:
            image = service.get('image')
            require(isinstance(image, str) and bool(image.strip()),
                    'Image-only service requires an explicit shared image.')
            candidates = [key for key, value in model.items() if isinstance(value, dict)
                          and value.get('image') == image and 'build' in value]
            require(len(candidates) == 1, 'Shared image requires exactly one build owner.')
            owner = candidates[0]
        require(isinstance(owner, str) and bool(owner.strip()), 'Invalid Compose build owner.')
        build = model[owner].get('build')
        require(isinstance(build, dict) and isinstance(build.get('context'), str)
                and bool(build['context'].strip()) and not build.get('additional_contexts')
                and not build.get('dockerfile_inline'),
                'Reserved build requires a local owned context and Dockerfile without additional contexts.')
        require(not build.get('tags'), 'Reserved build cannot export additional image tags.')
        require(not build.get('secrets') and not build.get('ssh'),
                'Reserved build cannot use auxiliary secrets or SSH inputs.')
        owners[name] = owner
    return owners


def freeze(repo: Path, revision: str, config: dict, expected_digest: str,
           output: Path, services: list[str]) -> Path:
    require(digest(config) == expected_digest, 'Evaluated Compose configuration differs from reviewed digest.')
    owners = resolve_build_owners(config, services)
    model = copy.deepcopy(config)
    snapshot = output / 'source'
    export_commit(repo, revision, snapshot)
    for name in services:
        service = model['services'][name]
        require(not service.get('env_file'), 'Evaluated Compose must resolve service env files.')
        require(all(value is not None for value in (service.get('environment') or {}).values()),
                'Evaluated Compose must resolve environment and build argument values.')
    for owner in sorted(set(owners.values())):
        build = model['services'][owner]['build']
        require(all(value is not None for value in (build.get('args') or {}).values()),
                'Evaluated Compose must resolve environment and build argument values.')
        context = Path(build['context']).resolve()
        dockerfile = Path(build.get('dockerfile', 'Dockerfile'))
        if not dockerfile.is_absolute():
            dockerfile = context / dockerfile
        try:
            context_relative = context.relative_to(repo.resolve())
            dockerfile_relative = dockerfile.resolve().relative_to(repo.resolve())
        except ValueError as exc:
            raise ValueError('Build input outside reviewed repository.') from exc
        exported_context = snapshot / context_relative
        exported_dockerfile = snapshot / dockerfile_relative
        require(exported_context.is_dir() and exported_dockerfile.is_file(),
                'Build context and Dockerfile must exist in the committed snapshot.')
        build['context'] = str(exported_context)
        build['dockerfile'] = str(exported_dockerfile)
    # `compose config` already doubles literal dollars for reuse, including JSON.
    # Preserve that representation; escaping again would change container values.
    path = output / 'compose.json'
    path.write_text(json.dumps(model, ensure_ascii=True), encoding='utf-8')
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['digest', 'resolve', 'freeze'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--repo')
    parser.add_argument('--revision')
    parser.add_argument('--digest')
    parser.add_argument('--output')
    parser.add_argument('--services', nargs='+')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    if args.action == 'digest':
        print(digest(config))
    elif args.action == 'resolve':
        try:
            require(args.digest and digest(config) == args.digest,
                    'Evaluated Compose configuration differs from reviewed digest.')
            print(json.dumps(resolve_build_owners(config, args.services)))
        except ReservationRefusal as exc:
            # Only bounded guard text crosses the adapter; no evaluated values.
            print(json.dumps({'refusal': str(exc)}))
            raise SystemExit(1) from None
    else:
        require(all((args.repo, args.revision, args.digest, args.output, args.services)),
                'Exact reviewed configuration/source and output required.')
        try:
            freeze(Path(args.repo), args.revision, config, args.digest, Path(args.output), args.services)
        except ReservationRefusal as exc:
            print(json.dumps({'refusal': str(exc)}))
            raise SystemExit(1) from None


if __name__ == '__main__':
    main()
