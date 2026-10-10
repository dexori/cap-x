# Third-party software and data

The repository's MIT License covers original CaP-X code. It does not replace the licenses or
terms of third-party software, model weights, robot assets, simulators, or datasets.

Git submodules are pinned to specific revisions from these upstream projects:

| Path | Upstream |
| --- | --- |
| `capx/third_party/LIBERO-PRO` | <https://github.com/uynitsuj/LIBERO-PRO> |
| `capx/third_party/b1k` | <https://github.com/qingh097/b1k> |
| `capx/third_party/contact_graspnet_pytorch` | <https://github.com/uynitsuj/contact_graspnet_pytorch> |
| `capx/third_party/curobo` | <https://github.com/NVlabs/curobo> |
| `capx/third_party/libero_dependencies/robosuite` | <https://github.com/Max-Fu/robosuite> |
| `capx/third_party/robosuite` | <https://github.com/uynitsuj/robosuite> |
| `capx/third_party/sam3` | <https://github.com/Max-Fu/sam3> |
| `capx/third_party/verl` | <https://github.com/Max-Fu/verl> |

Before redistributing a build or benchmark bundle, review the license file at each pinned
revision. Some optional setup paths also download model weights and datasets after presenting
separate access conditions or terms of service. In particular, NVIDIA Isaac Sim,
BEHAVIOR-1K assets, SAM model weights, LIBERO data, and hosted model APIs are not relicensed by
CaP-X.

If a third-party notice is missing or inaccurate, please open an issue with the component,
pinned revision, and relevant license source.
