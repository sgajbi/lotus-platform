# Recent Architectural Decisions Digest

This digest highlights recent decisions that materially affect current Lotus implementation practice.

It exists so a new session does not have to reconstruct current platform reality from many RFCs and pull requests.

## Current Effective Decisions

### RFC-0071 | Canonical environment-scoped service addressing and ingress governance

Current assumption:

1. local and non-prod runtime should prefer canonical `*.dev.lotus` addressing where supported,
2. ingress, hosts management, and service discovery are part of the platform contract,
3. validation and demo readiness should use canonical endpoints end-to-end.

### RFC-0072 | Multi-lane CI, validation, and release governance

Current assumption:

1. repositories are moving to explicit feature, PR merge, and main releasability lanes,
2. GitHub should be used as the heavy execution engine for expensive validation,
3. repo-native `make check` and `make ci` commands should match real lane truth,
4. workflow security, action baselines, container build rules, and release evidence are now governed platform concerns.

### Product and UI posture

Current assumption:

1. premium private-banking UI should be conservative, institutional, and information-dense without decorative noise,
2. summary first, detail on demand remains the product principle,
3. no UI feature should exist without real backend support,
4. numbers, clarity, and decision value should dominate over narrative or ornamental UI.

### Documentation and memory posture

Current assumption:

1. important working knowledge should not remain trapped in chat history,
2. platform-wide truth belongs centrally in `lotus-platform`,
3. repository truth belongs locally in each repo,
4. repeatable patterns should be promoted into standards, validators, templates, or skills.
