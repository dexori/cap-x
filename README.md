# CaP-X Experiments

基于 CaP-X 的个人机器人 Coding Agent 对比实验项目。

[![CI](https://github.com/dexori/cap-x/actions/workflows/ci.yml/badge.svg)](https://github.com/dexori/cap-x/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.12](https://img.shields.io/badge/Python-3.10%E2%80%933.12-blue.svg)](pyproject.toml)

> 这是 `dexori` 的个人实验仓库，不是 CaP-X 官方仓库。项目基于
> [capgym/cap-x](https://github.com/capgym/cap-x) 开展复现、模型对比和 Agent
> 策略实验；原始论文与作者信息见文末“上游项目与引用”。

## 项目目标

这个仓库用于在统一机器人任务和评测条件下，比较不同 Coding Agent、模型与交互策略：

- 不同语言模型或视觉语言模型的任务完成率；
- single-turn 与 multi-turn 调试能力；
- privileged state、视觉反馈和 Visual Differencing Module（VDM）的差异；
- high-level API、reduced API 与低层控制原语的差异；
- skill library、parallel ensemble 和 multimodel 策略的收益；
- Robosuite、LIBERO-PRO、BEHAVIOR 以及真实 Franka 环境中的迁移表现。

当前仓库保留了 CaP-X 的环境、评测器、感知服务和 Web UI，并增加了适合公开实验的
可复现协议、仓库检查和 CI。实验结果不会直接写进 README；每次正式对比应保留配置、
模型版本、Git commit 和完整输出目录。

## 实验矩阵

已有配置主要覆盖以下变量：

| 对比维度 | 配置示例 |
| --- | --- |
| Single-turn / Multi-turn | `franka_robosuite_cube_stack.yaml` / `franka_robosuite_cube_stack_multiturn.yaml` |
| 原始视觉反馈 / VDM | `*_multiturn_vf.yaml` / `*_multiturn_vdm.yaml` |
| 完整 API / Reduced API | 标准任务配置 / `*_reduced_api.yaml` |
| 无技能库 / Skill Library | `*_reduced_api.yaml` / `*_skill_lib.yaml` |
| 单模型 / Ensemble | 普通配置 / `hillclimb/ensemble_*.yaml` |
| 感知状态 / Privileged state | 普通配置 / `*_privileged.yaml` |

核心任务配置位于 `env_configs/`，包含 cube lifting、cube stack、cube restack、nut
assembly、spill wipe、two-arm lift、two-arm handover、LIBERO-PRO 和 BEHAVIOR 任务。

## 环境要求

- Linux x86_64
- Python 3.10（部分 LIBERO 环境使用独立的 Python 3.12 环境）
- `uv`
- NVIDIA CUDA GPU
- 至少一种受支持的仿真器
- OpenAI-compatible 模型接口，或本地 vLLM 服务

克隆项目和子模块：

```bash
git clone --recurse-submodules https://github.com/dexori/cap-x.git
cd cap-x

curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.10
uv venv --python 3.10
```

选择一种仿真器安装。Robosuite 与 LIBERO 使用不同版本的依赖，不要安装到同一个环境。

### Robosuite

```bash
uv sync --extra robosuite
```

### LIBERO-PRO

```bash
uv venv .venv-libero --python 3.12
source .venv-libero/bin/activate
uv sync --active --extra libero --extra contactgraspnet
```

### BEHAVIOR / OmniGibson

```bash
cd capx/third_party/b1k
./uv_install.sh --dataset
cd ../../..
```

BEHAVIOR 会单独要求接受 NVIDIA Isaac Sim 和数据集许可。详细步骤见
[BEHAVIOR 配置文档](docs/behavior-tasks.md)。

## 模型服务

评测器使用 OpenAI-compatible `/chat/completions` 接口。以 OpenRouter 代理为例：

```bash
echo "sk-or-v1-your-key-here" > .openrouterkey
uv run --no-sync --active capx/serving/openrouter_server.py \
  --key-file .openrouterkey \
  --port 8110
```

`.openrouterkey` 已加入 `.gitignore`。不要把密钥写入 YAML、日志或提交历史。

感知与运动规划服务通常会由任务 YAML 自动启动，也可以提前启动并由多个实验共享：

```bash
uv run --no-sync --active capx/serving/launch_servers.py --profile default
```

可用 profile：

| Profile | 服务 |
| --- | --- |
| `minimal` | PyRoKi |
| `default` | SAM3、ContactGraspNet、PyRoKi |
| `full` | default + OWL-ViT + SAM2 |

## 运行实验

### Single-turn 基线

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/cube_stack/franka_robosuite_cube_stack.yaml \
  --model "provider/versioned-model-id" \
  --temperature 1.0 \
  --total-trials 100 \
  --num-workers 12 \
  --output-dir ./outputs/experiments/single_turn
```

### Multi-turn + VDM

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/cube_stack/franka_robosuite_cube_stack_multiturn_vdm.yaml \
  --model "provider/versioned-model-id" \
  --total-trials 100 \
  --num-workers 8 \
  --output-dir ./outputs/experiments/multiturn_vdm
```

### Human oracle 环境检查

正式消耗模型额度之前，先运行人工参考策略确认仿真器、任务和成功判定正常：

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/human_oracle_code/robosuite/franka_robosuite_cube_stack_oracle.yaml \
  --use-oracle-code True \
  --total-trials 10 \
  --num-workers 1
```

### Web UI

```bash
uv run --no-sync --active capx/envs/launch.py \
  --config-path env_configs/cube_stack/franka_robosuite_cube_stack.yaml \
  --web-ui True
```

打开 <http://localhost:8200>。

## 结果与对比规范

输出目录会保存 `summaries.txt`，以及每个 trial 的生成代码、响应、日志、视觉反馈和
可选视频。公开对比时至少报告：

| 字段 | 说明 |
| --- | --- |
| Model | 精确模型或 checkpoint 标识，不只写模糊别名 |
| Task / Config | 使用的任务与 YAML 路径 |
| Git commit | 本次实验对应的代码版本与 dirty 状态 |
| Trials | 总 trial 数，失败和超时不能从分母移除 |
| Code generation success | 代码是否被评测器成功执行 |
| Average reward | 所有 trial 的平均环境奖励 |
| Task completed | 满足任务成功条件的 trial 数量 |
| Runtime settings | temperature、token budget、worker 数量和 GPU 环境 |

完整要求见[可复现对比协议](docs/reproducibility.md)。托管模型即使使用相同名字也可能
发生版本变化，正式实验应记录供应商和运行日期，并尽量进行多次完整重复实验。

## 快速检查

```bash
# 不依赖 GPU 的仓库检查
python scripts/check_repository.py
python -m compileall -q capx scripts tests verl_agent_reward

# Web UI
cd web-ui
npm ci
npm audit --audit-level=high
npm run build

# 需要 GPU、感知服务和模型代理
cd ..
./scripts/regression_test.sh quick
```

## 项目结构

```text
capx/                    核心环境、Agent 执行器、API 与服务
env_configs/             各任务和对比条件的 YAML 配置
scripts/                 回归实验、训练和结果处理脚本
tests/                   仿真器与集成测试
verl_agent_reward/       CaP-RL / GRPO 奖励实现
web-ui/                  React 交互界面
docs/                    安装、扩展和复现文档
```

## 文档

| 文档 | 内容 |
| --- | --- |
| [配置参考](docs/configuration.md) | YAML、CLI 参数与模型服务 |
| [可复现对比](docs/reproducibility.md) | 公平实验、产物与结果报告规范 |
| [开发指南](docs/development.md) | 测试、lint、checkpoint 与已知问题 |
| [添加环境](docs/adding-environments.md) | 新增仿真器和任务 |
| [添加 API](docs/adding-apis.md) | 新增机器人控制原语 |
| [LIBERO-PRO](docs/libero-tasks.md) | LIBERO 任务安装与运行 |
| [BEHAVIOR](docs/behavior-tasks.md) | OmniGibson / R1Pro 任务 |
| [CaP-RL](docs/rl-training.md) | VeRL / GRPO 训练 |
| [贡献指南](CONTRIBUTING.md) | 提交代码与实验结果的要求 |
| [安全说明](SECURITY.md) | 模型生成代码与机器人执行风险 |

## 上游项目与引用

本项目基于 [CaP-X 官方仓库](https://github.com/capgym/cap-x)。CaP-X 原始论文：

```bibtex
@article{fu2026capx,
  title   = {{CaP-X}: A Framework for Benchmarking and Improving Coding Agents for Robot Manipulation},
  author  = {Fu, Letian and Yu, Justin and El-Refai, Karim and Kou, Ethan and Xue, Haoru and Huang, Huang and Xiao, Wenli and Wang, Guanzhi and Niu, Dantong and Li, Fei-Fei and Shi, Guanya and Wu, Jiajun and Sastry, Shankar and Zhu, Yuke and Goldberg, Ken and Fan, Linxi},
  journal = {arXiv preprint arXiv:2603.22435},
  year    = {2026},
  url     = {https://arxiv.org/abs/2603.22435}
}
```

个人实验改动由 `dexori` 维护。上游代码、第三方仿真器、模型权重和数据集分别遵循各自
许可证，详见 [THIRD_PARTY.md](THIRD_PARTY.md)。

## License

本仓库代码按 [MIT License](LICENSE) 发布。
