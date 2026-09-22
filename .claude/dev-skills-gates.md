# Dev Skills gate state
Track: release sequence
Mode: manual
Version: 0.1.0
Repo: darthrater78/ha-clawdmeter (fork; upstream = corgan2222/ha-clawdmeter)
Updated: 2026-09-22

🔢 VERSION    ✅ manifest.json 0.1.0 (only version-carrying file)
  MINOR chosen by user: new surface sensors + Sonnet/Opus deprecation.
  v0.0.1 / v0.0.2 copied from upstream to the fork (same commits).
  documentation / issue_tracker / codeowners → darthrater78 (user choice).
🔨 BUILD      ➖ N/A — HA custom integration, no build step
  pytest 74 passed, 100% coverage; ruff clean (py3.14 venv)
🔒 SECURITY   ✅ 0 open — code scan clean on the release diff
  F1 WAIVED (user, 2026-09-22): test-only deps (PHACC 0.13.340; cryptography
      pinned by HA core) carry PYSEC advisories; nothing shipped
      (requirements: []). Harness bump → Dependabot PR. Re-opens if that changes.
📄 DOCS       ✅ README: surface sensors, deprecation note, fork links
  Version history = Release Drafter notes (no CHANGELOG), approved at Gate 5.
📦 RELEASE    ✅ commit approved; PR into darthrater78:main
🚀 SHIP       ⏳ plan: merge PR → user pushes v0.1.0 → release.yml publishes
  First run of the tag-driven release.yml (merged in fork PR #1, d7a5157).

## Shipped
- fork PR #1 ci/tag-driven-release → d7a5157 (work commit, no release)
