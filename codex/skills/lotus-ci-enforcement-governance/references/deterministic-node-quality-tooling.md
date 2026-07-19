# Deterministic Node Quality Tooling

Use this reference when a blocking quality gate uses a Node-based tool.

## Lock-backed package contract

Keep dependency resolution reproducible:

1. own the tool in a capability-named package such as `tools/api_governance/`, not in a root-level
   file dump;
2. declare direct quality-tool dependencies with exact versions and commit the adjacent
   `package-lock.json`;
3. declare an exact or bounded supported Node range and configure the same governed Node release in
   CI;
4. restore dependencies with `npm ci`, preferably with lifecycle scripts disabled when the tool
   does not need them;
5. invoke the lock-installed `node_modules/.bin` executable or an owned package script;
6. run the applicable dependency vulnerability audit and fix or explicitly govern findings before
   treating the output as release evidence.

## Forbidden mutable-resolution patterns

Do not use unversioned `npx`, implicit latest tags, global npm installs, or mutable `npm install`
resolution as blocking PR, main, release, provenance, or certification evidence.

An explicitly report-only inventory may retain a pinned bootstrap fallback while it converges, but
it is not release evidence and must not be promoted without the lock-backed package contract above.

## Validation

Validate applicable repositories with:

```powershell
python automation/quality_tooling/validate_node_quality_tooling.py --repository <repo-root>
```

Do not add Node to a Python-only service scaffold merely to satisfy this rule. Keep the scaffold
dependency surface minimal and require it to pass the validator; add an owned Node tooling package
only when the generated service gains a real Node-based blocking gate.
