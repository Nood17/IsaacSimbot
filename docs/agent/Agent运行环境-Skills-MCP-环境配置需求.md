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

### 3.1 硬件与驱动

| 项 | 值 |
|---|---|
| 宿主机 | Windows + **WSL2**（DESKTOP-9S36E5P） |
| GPU | **RTX 4070 Ti 12GB**（Ada / sm_89） |
| 驱动 / CUDA | 591.74 / CUDA 13.1 |
| 仓库位置 | WSL `~/仿真/IsaacSimbot`（= Windows `I:\仿真\IsaacSimbot`，git remote 指向 `Nood17/IsaacSimbot`） |

### 3.2 软件栈（conda `env_isaaclab`）

| 组件 | 版本/状态 |
|---|---|
| Python | 3.11.16 |
| Isaac Sim | 5.1.0.0（pip 安装） |
| Isaac Lab | @3c6e67bb（editable） |
| torch | 2.7.0+cu128 |
| rsl-rl-lib | 3.0.1 |
| unitree_rl_lab | @4960b847（editable，0.2.1） |
| 已验证吞吐 | headless 4096 envs ≈ 28k steps/s，~3.5s/iter |

### 3.3 必须的环境变量与激活

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
# activate.d/setenv.sh 自动导出以下三项；手动复现时缺一不可：
export ISAACLAB_PATH=~/仿真/IsaacLab
export OMNI_KIT_ACCEPT_EULA=YES                      # 非交互运行必需
export LD_LIBRARY_PATH=~/仿真/wsl_lib_links:/usr/lib/wsl/lib:$CONDA_PREFIX/lib
```

**LD_LIBRARY_PATH 为何必需**：PhysX GPU 初始化需要无版本号的 `libcuda.so`，WSL 原生 `/usr/lib/wsl/lib` 只提供 `libcuda.so.1`。缺失时进程**在加载 USD 阶段静默退出、无 traceback**——这是本环境最坑的故障模式。

### 3.4 WSL2 特有问题清单

1. `~/仿真/wsl_lib_links/`（libcuda.so、libnvidia-ml.so 软链）**勿删**
2. 缺 X11/GLU：已 conda 装 `libglu`、`xorg-libxt`（无 sudo，apt 不可用）
3. Vulkan/渲染不可用属正常（"No device could be created"）——headless 训练不受影响；可视化播放需 Windows 端 Isaac Sim 或原生 Linux
4. `egl_probe`/`flatdict` 编译需要 conda 的 `gxx_linux-64` 与 `setuptools==80.9.0` + `--no-build-isolation` + `CMAKE_POLICY_VERSION_MINIMUM=3.5`
5. WSL DNS 间歇失败 → pip 用 `--resume-retries` 重试脚本；git 已配 `ghfast.top` 镜像 insteadOf
6. pip 装包必须带 `PIP_CONSTRAINT=/mnt/i/仿真/constraints.txt`——防依赖解析抢装新版 torch 把 cu128 顶掉
7. exec 工具会预展开 `$var`/`$(...)`——复杂命令写进脚本文件再跑

### 3.5 快速验证

```bash
conda activate env_isaaclab && cd ~/仿真/unitree_rl_lab
python scripts/list_envs.py            # 应列出全部已注册任务
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity --num_envs 64 --headless --max_iterations 5   # 冒烟
```

### 3.6 Devin CLI 侧依赖

- `devin` v3000.11.3 @ `~/.local/bin/devin`；WSL 侧需单独 `devin auth login` 一次（未登录时 `devin -p` 会挂死在登录 TUI，runner 已做前置检查）
- `jq` 1.8.1 静态二进制 @ `~/.local/bin/jq`
- `systemctl --user` 可用，linger 已开；迭代单元 `bmmms-*`/`iteration.*`/`watchdog.*`

## 4. 一页速查

```bash
# 进环境
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
cd ~/仿真/unitree_rl_lab

# 任务 A 主线训练
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity --num_envs 4096 --headless

# 体检
nvidia-smi && python scripts/list_envs.py | grep Unitree
```

- Skills 清单 → §1；MCP 现状=未配置，格式 → §2；环境坑 → §3.4
- 详细坑位与修复历史见根目录 `AGENTS_WSL2_NOTES.md`
