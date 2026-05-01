# Integrations

## What `lotus-platform` integrates with

`lotus-platform` is connected to the entire Lotus ecosystem through governance, validation,
automation, and runtime support.

## Primary integration relationships

- `lotus-workbench`
  canonical front-office runtime, QA wrapper support, panel and screenshot evidence governance
- `lotus-gateway`
  ingress, platform validation support, and product-facing integration governance; current Gateway
  proposal flows target `lotus-advise` `/advisory/proposals*`, while Gateway `lotus-manage`
  consumption is limited to versioned strategic run lookup, supportability summary, and capability
  posture
- `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, `lotus-render`, `lotus-archive`, `lotus-ai`
  standards validation, repo checks, automation registration, and cross-app validation support

## Integration surfaces

- repo-native check wrappers
- cross-app validation scripts
- automation manifests and repository inventory
- ingress host mappings
- context and skill distribution

## Important rule

Platform integration should centralize cross-repo governance once, instead of encouraging each repo
to reinvent the same operator workflows.

## Legacy documentation boundary

When historical documentation was written under one application repo but actually describes Lotus as
an ecosystem, it should be reclassified and moved into `lotus-platform`.

See:

- [Legacy Core Wiki Migration Ledger](Legacy-Core-Wiki-Migration-Ledger)
