# Contributing

Thanks for helping improve Clawdmeter!

## Branch policy

`main` is protected and **cannot be pushed to directly** — every change goes through a pull
request:

1. Create a branch and commit your change there.
2. Open a pull request against `main`.
3. CI must pass: **Ruff** (lint + format), **Pytest** (tests), **Hassfest** and **HACS**
   (validation).
4. Merge once all checks are green.

Force-pushing to and deleting `main` are disabled for everyone.

## Development

Tests use
[pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component):

```bash
pip install -r requirements_test.txt
pytest tests/
ruff check .
ruff format --check .
```

After a notable change, bump `version` in `custom_components/clawdmeter/manifest.json`.

## Releasing

Release notes are drafted automatically by Release Drafter from merged pull requests
(labels decide the section). To publish a release:

1. Merge a pull request that bumps `version` in `custom_components/clawdmeter/manifest.json`.
2. Tag the merged commit on `main` with the same version and push the tag:

   ```bash
   git checkout main && git pull
   git tag v0.1.0
   git push origin v0.1.0
   ```

The **Release** workflow then checks the tag is on `main`, matches `manifest.json` and
that CI passed on that commit, publishes the drafted release and attaches
`clawdmeter.zip`. Don't publish the draft by hand — push the tag instead.
