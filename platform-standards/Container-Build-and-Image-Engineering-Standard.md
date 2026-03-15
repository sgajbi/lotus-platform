# Container Build and Image Engineering Standard

## Purpose
Define the minimum standard for Docker build performance, reproducibility, and runtime image hygiene across Lotus backend repositories.

## Scope
Applies to all Lotus backend repositories that publish Docker images or run Docker-backed CI gates.

## Required Standards

### 1. Build Context Hygiene
Every repo must maintain a `.dockerignore` that excludes at least:
- `.git`
- local virtualenvs and caches
- test artifacts and coverage output
- `docs/` unless build-time docs are required
- `tests/` unless test assets are copied into images

Do not rely on `.gitignore` alone.

### 2. Deterministic Dependencies
Docker and CI builds must not resolve open-ended dependencies directly from floating version ranges at build time.

Required:
- pinned direct runtime dependencies
- a lock or compiled dependency artifact for reproducible builds
- base images pinned by major/minor and preferably digest for production releases

### 3. Multi-Stage Images
Production images must use multi-stage builds.

Required split:
- builder stage for dependency installation and wheel/build work
- runtime stage containing only the runtime environment and required app assets

Do not ship compilers or build toolchains in final runtime images unless operationally required.

### 4. Layer Ordering
Dockerfiles must order layers to maximize cache reuse:
1. base OS/runtime setup
2. dependency metadata and lock files
3. dependency install
4. application source copy
5. final runtime-only copy

Do not copy the full source tree before dependency installation unless there is no viable alternative.

### 5. BuildKit Cache Mounts
Python service Dockerfiles should use BuildKit cache mounts for package installation steps.

Required when BuildKit is enabled:
- `# syntax=docker/dockerfile:1.7`
- `RUN --mount=type=cache,target=/root/.cache/pip ...`

This is the minimum standard for repeated image builds in smoke, latency, performance, and recovery gates.

### 6. Shared Build Pattern
Repositories with multiple Python services must standardize Dockerfile structure across services.

Required:
- common base-stage conventions
- common runtime user model
- common healthcheck pattern where applicable
- no service-local drift for install mechanics unless justified

### 7. CI Build Acceleration
GitHub Actions workflows that build Docker images must enable:
- `DOCKER_BUILDKIT=1`
- `COMPOSE_DOCKER_CLI_BUILD=1` when docker compose builds are used
- `docker/setup-buildx-action` for Docker build jobs

Where builds are frequent or expensive, use cache import/export rather than rebuilding cold each run.

### 8. Local-Dev vs Production Split
Developer convenience images and production images are different concerns.

Allowed:
- separate Dockerfiles or targets for local editable workflows

Required:
- production images remain optimized for reproducibility, minimal attack surface, and startup determinism

### 9. Runtime Image Hygiene
Production images must:
- run as non-root
- include only required runtime files
- avoid unnecessary package managers and build tools in final stage
- expose only required ports

### 10. Evidence and Governance
Each repository must be able to point to:
- Docker build workflow
- `.dockerignore`
- runtime image Dockerfiles
- documented repo-specific deviations from this standard

## Recommended Rollout Order
1. `.dockerignore`
2. BuildKit + buildx enablement in CI
3. multi-stage Dockerfiles
4. dependency locking / compiled requirements
5. shared templates across repositories
6. registry-backed cache and provenance/SBOM expansion

## Anti-Patterns
- single-stage production images when build steps are non-trivial
- copying the entire repository into images without a strong `.dockerignore`
- repeated online dependency resolution in every CI job
- floating dependency resolution in release builds
- service Dockerfiles drifting without a documented reason
