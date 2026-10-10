# Reproducible comparisons

CaP-X results depend on the simulator, task configuration, perception services, model provider,
and sampling settings. A model name and success percentage alone are not enough to reproduce a
comparison. Use this protocol for benchmark runs and public result reports.

## 1. Freeze the experiment

Record the following before running:

- the CaP-X Git commit and whether the worktree is clean;
- every submodule revision (`git submodule status --recursive`);
- the simulator family, dataset/task version, GPU model, driver, and CUDA version;
- the exact YAML file, including any local edits;
- the code-generation and visual-differencing provider, exact model identifier or checkpoint,
  endpoint implementation, and run date;
- `temperature`, `max_tokens`, `reasoning_effort`, worker count, and trial count; and
- which optional services and model weights were used for segmentation, grasping, and planning.

Use the checked-in `uv.lock` and do not update dependencies between compared runs. Preserve a
copy of a modified config with the results instead of relying only on CLI history.

## 2. Keep comparison conditions equal

For an A/B comparison, change only the factor named in the hypothesis. In particular, use the
same task configs, trial IDs, cameras, control APIs, perception servers, prompt, token budget,
and success predicate. CaP-X launches trial IDs from 1 through `total_trials`; environments use
the trial ID as their seed or task-instance selector where supported.

Hosted models can change behind a stable alias and may be nondeterministic at any temperature.
Prefer versioned model identifiers. When that is impossible, record the provider and timestamp
and repeat the complete run enough times to show variation rather than reporting extra decimal
places from one run.

## 3. Run and retain artifacts

Start the chosen OpenAI-compatible model proxy as described in
[Configuration](configuration.md), then run a config without editing it in place:

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/cube_stack/franka_robosuite_cube_stack.yaml \
  --model "provider/versioned-model-id" \
  --temperature 1.0 \
  --total-trials 100 \
  --num-workers 12 \
  --output-dir ./outputs/reproduction/single_turn
```

The launcher inserts a filesystem-safe model name into the configured output path. The output
contains `summaries.txt` plus per-trial directories named with the sandbox return code, reward,
and completion result. Depending on the config, each trial can contain generated code, raw
responses, prompts, execution logs, feedback images, and video.

Run the human-written policy before spending model credits to validate the simulator and task:

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/human_oracle_code/robosuite/franka_robosuite_cube_stack_oracle.yaml \
  --use-oracle-code True \
  --total-trials 10 \
  --num-workers 1
```

The maintained cube-stack smoke and regression checks are available through:

```bash
./scripts/regression_test.sh quick
./scripts/regression_test.sh test1
./scripts/regression_test.sh test2
```

These checks need the Robosuite environment, perception services, and a model proxy. Their
thresholds detect large regressions; they are not statistical claims about model quality.

## 4. Report results

At minimum, publish:

| Field | Meaning |
| --- | --- |
| Code generation success rate | Fraction of trials whose generated program executed according to the harness |
| Average reward | Mean environment reward over all executed trials |
| Task completed | Count of trials satisfying the environment's task predicate |
| Trials | Denominator for all aggregate values, including timeouts and failures |
| Agent interaction | Single-turn, visual feedback, VDM, ensemble, or other enabled mode |
| Provenance | Git commit, dirty state, config, model identifiers, provider, and run date |

Include uncertainty across repeated runs when making comparative claims. Keep failed trials and
timeouts in the denominator, and disclose retries, provider failures, excluded trials, or manual
intervention.

## 5. Share safely

Before publishing output artifacts, inspect them for API keys, private endpoint URLs, personal
data, proprietary prompts, and assets whose licenses prohibit redistribution. Generated Python
is untrusted code; do not execute an artifact downloaded from someone else without reviewing it
and isolating the process. See [SECURITY.md](../SECURITY.md) and
[THIRD_PARTY.md](../THIRD_PARTY.md).
