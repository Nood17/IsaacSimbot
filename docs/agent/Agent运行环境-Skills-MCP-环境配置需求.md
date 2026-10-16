# Agent 运行环境：Skills / MCP / 环境配置需求

> 2026-10-15 整理。面向在 IsaacSimbot 工作区中运行的 AI Agent（Devin CLI）与人维护者。
> 目的：让任何新会话/新机器能快速复现"Agent 可用 + 训练可跑"的完整环境。

---

## 1. Skills（技能）

### 1.1 本仓库已安装的技能（`.devin/skills/`）

| Skill | 用途 | 触发场景 |
|---|---|---|
| `academic-paper` | 12-agent 论文写作管线：11 种模式（全文/大纲/修订/摘要/文献综述/格式转换/引用检查/AI 披露/反驳信审计），6 种论文类型，5 种引用格式，LaTeX/Pandoc-DOCX/PDF 输出 | 写论文、修审稿意见、引用核对 |
| `academic-paper-reviewer` | 5 席角色分离评审面板（期刊匹配 + 3 个同行评审角色 + 魔鬼代言人），支持复审与校准 | 模拟审稿、预审 manuscript |
| `academic-pipeline` | 端到端编排器：研究 → 写作 → 完整性检查 → 评审 → 修订 → 终审，10 阶段流水线 | 从调研到成稿的全流程 |
| `deep-research` | 13-agent 深度研究管线：系统性文献检索、来源核验、偏倚评估、元分析、APA 报告 | 调研课题、文献综述、事实核查 |
| `research-paper-pipeline` | CS 顶会全流程：选题 → 文献 → 方法 → 实验 → 写作 → 模拟审稿 → Rebuttal | 中文场景顶会论文全流程 |

**结构约定**：每个技能是 `.devin/skills/<name>/SKILL.md` + 附属目录（`agents/`、`references/`、`scripts/`、`templates/` 等）。新增技能一律放 `.devin/skills/`；全局技能放 `~/.config/devin/`；不要写进 `.claude/`、`.cursor/` 等兼容目录。

**调用方式**：会话中由 `skill` 工具按名称 invoke；同名触发词命中时自动激活。仓库技能与会话级技能（如其他工作区 `.agents/skills/`）可能同时可见，注意区分来源路径。

### 1.2 迭代循环机制（`.devin/`）

- `iteration-prompt.md`：每轮会话注入的任务提示词（当前主线 = 任务 A Go2 复杂地形）
- `handoff.md`：轮间交接，最新状态写顶部，使命完成写 `MISSION-COMPLETE`
- `loop/`：旧版巡检循环机制（`run-iteration.sh`、`watchdog.sh`、systemd 单元模板）
- ⚠️ `iteration.timer`/`watchdog.timer` 已于 2026-10-15 停用；恢复前确认使命并执行 `systemctl --user enable --now iteration.timer watchdog.timer`

## 2. MCP（Model Context Protocol）

**本仓库当前未配置任何 MCP server**。需要时在仓库根创建 `.devin/mcp_config.json`，格式：

```json
{
  "mcpServers": {
    "<name>": {
      "url": "https://<host>/mcp"            // 远程 server
    },
    "<name>": {
      "command": "<cmd>",                     // 本地 stdio server
      "args": ["..."]
    }
  }
}
```

参考样例（`~/CANN/.devin/mcp_config.json`，不属本仓库）：context7、deepwiki、wolfram（远程 URL）；playwright（本地 docker command）。

**本项目的可选方向**（按需再加，不是现状）：
- `context7` / `deepwiki`：查 Isaac Lab / rsl_rl 最新 API 文档
- GitHub MCP：仓库 issue/PR 操作（本仓库推送走 git+`gh` 已够用）

用户级配置在 `~/.config/devin/config.json`（当前仅有 org_id 与 agent 参数，无 MCP 段）。

## 3. 环境配置需求

### 3.1 三设备一览（⚠️ 仓库在多台机器间同步，先确认自己在哪台）

| | **本机 5060** `robot` | **5090 训练机** `ubuntu-System-Product-Name` | **WSL2** `DESKTOP-9S36E5P` |
|---|---|---|---|
| 系统 | Ubuntu 26.04 原生 | Ubuntu 原生（桌面） | Windows + WSL2 |
| GPU | RTX 5060 Laptop **8GB**（sm_120） | RTX 5090 | RTX 4070 Ti **12GB**（sm_89） |
| 驱动 | 580.178.04 | 未核实 | 591.74 / CUDA 13.1 |
| 仓库路径 | `/home/nood/IsaacSimbot` | `/home/ubuntu/nood/…`（待核实） | `~/仿真/IsaacSimbot`（= `I:\仿真\…`） |
| IsaacLab 路径 | `~/仿真/IsaacLab`（editable） | 未核实 | `~/仿真/IsaacLab` |
| 角色 | 开发/文档/面板 | 主训练机（Go2 A1 在此跑） | 训练 + 历史实验 |
| 已验证吞吐 | 未实测（8GB 显存，4096 envs 大概率 OOM，建议 ≤2048 起步） | Go2 A1 v2 完成 8465 iter | 4096 envs ≈ 28k steps/s |

**判断自己在哪台**：`hostname` + `nvidia-smi` + 仓库路径，三者一对即知。commit `0970b57` 里出现 `/home/ubuntu/nood/` 路径即 5090 机的痕迹——写脚本时用环境名/相对路径，别写死某台机器的绝对路径。

### 3.2 共享软件栈（conda `env_isaaclab`，三机同名）

| 组件 | 版本/状态 |
|---|---|
| Python | 3.11.16 |
| Isaac Sim | 5.1.0.0（pip 安装） |
| Isaac Lab | editable（本机实测 0.47.2 @ `~/仿真/IsaacLab`） |
| torch | 2.7.0+cu128 |
| rsl-rl-lib | 3.0.1 |
| unitree_rl_lab | editable（仓库内 `unitree_rl_lab/`，随 repo HEAD） |
| numpy | 1.26.0 |

### 3.3 通用激活（三机相同，按环境名激活、勿用绝对路径）

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab        # 按名字，不依赖机器路径
export OMNI_KIT_ACCEPT_EULA=YES    # 非交互运行必需
```

`lunar_panel.py` 的 `ENV_ACT` 同理——曾写成 5090 机的 `/home/ubuntu/nood/env_isaaclab` 绝对路径，已改回按名激活。

### 3.4 WSL2 设备专属问题（仅第三台机器适用）

以下坑**只存在于 WSL2 设备**，5060/5090 原生 Ubuntu 不受此影响：

1. `LD_LIBRARY_PATH` 必须含 `~/仿真/wsl_lib_links:/usr/lib/wsl/lib:$CONDA_PREFIX/lib`——PhysX GPU 要无版本号 `libcuda.so`，WSL 只给 `.so.1`，缺失时进程在加载 USD 阶段**静默退出、无 traceback**
2. `~/仿真/wsl_lib_links/`（libcuda.so、libnvidia-ml.so 软链）**勿删**
3. 缺 X11/GLU：已 conda 装 `libglu`、`xorg-libxt`；Vulkan/渲染不可用属正常，可视化播放需 Windows 端或另两台原生机
4. `egl_probe`/`flatdict` 编译需 conda `gxx_linux-64` + `setuptools==80.9.0` + `--no-build-isolation` + `CMAKE_POLICY_VERSION_MINIMUM=3.5`
5. WSL DNS 间歇失败 → pip `--resume-retries`；git 配 `ghfast.top` insteadOf
6. pip 装包带 `PIP_CONSTRAINT=/mnt/i/仿真/constraints.txt` 防 torch 被顶掉
7. 详细修复历史见根目录 `AGENTS_WSL2_NOTES.md`（**该文件仅描述 WSL 设备**）

### 3.5 各设备注意事项

- **本机 5060**：原生桌面，`DISPLAY=:0` 直接弹 tkinter/Isaac GUI；8GB 显存跑训练前先把 `--num_envs` 降下来；GPU PhysX 冒烟尚未实测
- **5090**：路径前缀 `/home/ubuntu/nood`；训练产出的 run 目录/events 通过 git 归档回仓库
- **WSL2**：见 §3.4；无原生显示（GUI 需 WSLg 或 X Server）

### 3.6 快速验证（任意机器）

```bash
conda activate env_isaaclab && cd <repo>/unitree_rl_lab
python scripts/list_envs.py            # 应列出全部已注册任务
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity --num_envs 64 --headless --max_iterations 5   # 冒烟
```

### 3.7 Devin CLI 侧依赖（WSL 设备）

- `devin` v3000.11.3 @ `~/.local/bin/devin`；WSL 侧需单独 `devin auth login` 一次
- `jq` 1.8.1 静态二进制 @ `~/.local/bin/jq`
- `systemctl --user` 可用，linger 已开；迭代单元 `bmmms-*`/`iteration.*`/`watchdog.*`（仅 WSL 机上配置过）

## 4. 一页速查

```bash
# 先确认自己在哪台机器
hostname && nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# 进环境（三机通用）
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
cd <repo>/unitree_rl_lab     # 5060: ~/IsaacSimbot；WSL: ~/仿真/IsaacSimbot；5090: /home/ubuntu/nood/…

# 任务 A 主线训练（num_envs 按显存调：5090/4070Ti 可 4096，5060 建议 ≤2048）
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity --num_envs 4096 --headless
```

- Skills 清单 → §1；MCP 现状=未配置，格式 → §2；设备区分 → §3.1；WSL 专属坑 → §3.4
