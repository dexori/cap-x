# Contributing to CaP-X

Thanks for helping improve CaP-X. Contributions may include bug fixes, new tasks or robot
APIs, documentation, reproducibility reports, and benchmark tooling.

## Before you start

- Search existing issues and pull requests before opening a duplicate.
- Use an issue to discuss changes that alter benchmark semantics, public APIs, dependencies,
  or result formats before investing in an implementation.
- Do not include model credentials, private datasets, generated outputs, or third-party assets
  that cannot be redistributed.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) and report vulnerabilities through the
  private process in [SECURITY.md](SECURITY.md), not a public issue.

## Development setup

Clone the submodules and create the base Python 3.10 environment:

```bash
git clone --recurse-submodules https://github.com/dexori/cap-x.git
cd cap-x
uv python install 3.10
uv venv --python 3.10
uv sync --extra dev
```

Simulator families have conflicting dependencies. Install only the extra required for the
area you are changing:

```bash
uv sync --extra dev --extra robosuite
# or use the separate LIBERO environment described in README.md
```

For web UI changes:

```bash
cd web-ui
npm ci
npm run dev
```

## Making a change

Keep a pull request focused. Add or update tests and documentation when behavior changes.
New benchmark tasks should include:

1. A deterministic task/environment definition where the simulator permits it.
2. A YAML configuration under `env_configs/` with no machine-specific paths or credentials.
3. Success criteria and a human/oracle sanity check.
4. Documentation of required assets, simulator version, cameras, seeds, and expected output.

See [Adding Environments](docs/adding-environments.md), [Adding APIs](docs/adding-apis.md), and
the [reproducibility guide](docs/reproducibility.md) for the relevant contracts.

## Checks

Run the checks that match your change:

```bash
# Fast checks used by CI
python -m compileall -q capx scripts tests verl_agent_reward
python scripts/check_repository.py

# Python style (the repository is adopting these checks incrementally)
uv run ruff check <changed-python-files>

# Frontend
cd web-ui && npm ci && npm run build

# Hardware-dependent regression, after starting the required model proxy
./scripts/regression_test.sh quick
```

The full simulator tests are intentionally not part of hosted CI because they require GPUs,
licensed assets, model access, and long-running services. In the pull request, state exactly
which simulator tests you ran and include the command, GPU/simulator setup, model identifier,
trial count, and summary. If you could not run a relevant test, say so plainly.

## Pull requests

- Explain the problem and the user-visible effect of the solution.
- Link related issues.
- Call out changes to task definitions, prompts, success conditions, seeds, or model settings;
  these can invalidate benchmark comparisons even when the code change is small.
- Do not mix generated artifacts or broad formatting changes into a functional patch.
- Confirm that new dependencies have compatible redistribution terms.

By contributing, you agree that your contribution is licensed under the repository's
[MIT License](LICENSE).
