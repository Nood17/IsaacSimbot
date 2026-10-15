#!/usr/bin/env python
"""Lunar locomotion training control panel.

Single-file tkinter GUI for the Unitree-G1 lunar-surface experiments.

  Left   : all tunable knobs, grouped by section. Values are read directly from
           the env/agent cfg source files and written back in-place (one .bak
           backup per file is kept next to it). Changes apply to the NEXT run.
  Right  : run control -- pick experiment, pick a checkpoint (or scratch),
           start / stop training, launch play.py for visual inspection.
  Bottom : live metrics parsed from the training log (last metric block plus a
           reward / tracking / curriculum history plot).

Usage:
    source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
    python /home/nood/IsaacSimbot/lunar_panel.py
"""

from __future__ import annotations

import glob
import os
import re
import signal
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.join(BASE, "unitree_rl_lab")
SRC = os.path.join(LAB, "source/unitree_rl_lab/unitree_rl_lab")
VEL_CFG = os.path.join(SRC, "tasks/locomotion/robots/g1/29dof/velocity_env_cfg.py")
LSURF_CFG = os.path.join(SRC, "tasks/locomotion/robots/g1/29dof/lunar_surface_env_cfg.py")
TERRAIN_PY = os.path.join(SRC, "tasks/locomotion/lunar_terrain.py")
PPO_CFG = os.path.join(SRC, "tasks/locomotion/agents/rsl_rl_ppo_cfg.py")
LOGROOT = os.path.join(LAB, "logs/rsl_rl/unitree_g1_29dof_velocity_lunarsurface")
OLD_LOGROOT = os.path.join(LAB, "logs/rsl_rl/unitree_g1_29dof_velocity")
TASK = "Unitree-G1-29dof-Velocity-LunarSurface"
ENV_ACT = "source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab"

# --------------------------------------------------------------------------
# Knob registry.
# Each knob: (section, label, file, key_regex, fmt, help)
#   key_regex must contain exactly ONE capture group = the editable value text.
#   fmt: how to render a string back into the file ("raw" | "tuple" | "neg")
# --------------------------------------------------------------------------
KNOBS = [
    # ---- physics ---------------------------------------------------------
    ("物理仿真", "月面重力 sim.gravity (m/s²)", VEL_CFG,
     r"self\.sim\.gravity\s*=\s*\(0\.0,\s*0\.0,\s*(-?[\d.]+)\)", "raw",
     "负值向下。月面 -1.62，地球 -9.81。改动影响两个任务（共享 cfg）。"),
    ("物理仿真", "物理步长 sim.dt (s)", VEL_CFG,
     r"self\.sim\.dt\s*=\s*([\d.]+)", "raw",
     "默认 0.005 → 物理 200Hz。"),
    ("物理仿真", "decimation（策略降采样）", VEL_CFG,
     r"self\.decimation\s*=\s*(\d+)", "raw",
     "每 N 个物理步推理一次。4 → 策略 50Hz。"),
    ("物理仿真", "单回合时长 episode_length_s", VEL_CFG,
     r"self\.episode_length_s\s*=\s*([\d.]+)", "raw",
     "20s = 1000 策略步上限。"),
    ("物理仿真", "PhysX gpu_collision_stack_size", LSURF_CFG,
     r"gpu_collision_stack_size\s*=\s*(2\*\*\d+|\d+)", "raw",
     "4096 envs 下保持 2**26；2**27 会 OOM！"),
    ("物理仿真", "max_init_terrain_level", LSURF_CFG,
     r"max_init_terrain_level\s*=\s*([^\n]+?)\n", "raw",
     "初始允许的最高难度行，默认 num_rows-1。"),

    # ---- terrain ---------------------------------------------------------
    ("月面地形", "补丁尺寸 size (m)", LSURF_CFG,
     r"size=\(([\d.,\s]+)\)", "tuple",
     "单块地形边长，当前 (32.0, 32.0)。"),
    ("月面地形", "难度行数 num_rows", LSURF_CFG,
     r"num_rows=(\d+)", "raw", "课程难度分级数，当前 9。"),
    ("月面地形", "类型列数 num_cols", LSURF_CFG,
     r"num_cols=(\d+)", "raw", "每行多少种地形，当前 10。"),
    ("月面地形", "生成种子 seed", LSURF_CFG,
     r"\bseed=(\d+)", "raw", "固定 42 → 三实验地形逐比特一致。"),
    ("月面地形", "DEM 比例 proportion", LSURF_CFG,
     r"LunarDemTerrainCfg\(proportion=([\d.]+)\)", "raw",
     "真实月面地形占比，其余为平地（配比旋钮）。"),
    ("月面地形", "目标坡度范围 slope_range (deg)", TERRAIN_PY,
     r"slope_range:\s*tuple\[float,\s*float\]\s*=\s*\(([\d.,\s]+)\)", "tuple",
     "难度 0→1 映射到的平均坡度区间，当前 (0, 25)。"),
    ("月面地形", "微起伏幅度 micro_relief (m)", TERRAIN_PY,
     r"micro_relief:\s*tuple\[float,\s*float\]\s*=\s*\(([\d.,\s]+)\)", "tuple",
     "月壤噪声峰幅，随难度线性增，当前 (0, 0.10)。"),
    ("月面地形", "陨坑数 crater_count /patch", TERRAIN_PY,
     r"crater_count:\s*tuple\[float,\s*float\]\s*=\s*\(([\d.,\s]+)\)", "tuple",
     "难度 0→1 的小陨坑个数，当前 (0, 6)。"),
    ("月面地形", "网格顶点间距 horizontal_scale (m)", TERRAIN_PY,
     r"horizontal_scale:\s*float\s*=\s*([\d.]+)", "raw",
     "mesh 顶点间隔，越小越精细越慢，当前 0.2。"),
    ("月面地形", "DEM 分辨率 dem_resolution (m/px)", TERRAIN_PY,
     r"dem_resolution:\s*float\s*=\s*([\d.]+)", "raw", "LOLA 5mpp = 5.0。"),

    # ---- commands / curriculum ------------------------------------------
    ("指令与课程", "初始速度指令范围 ranges", VEL_CFG,
     r"lin_vel_x=\(([-\d.,\s]+)\),\s*lin_vel_y=\(([-\d.,\s]+)\),\s*ang_vel_z=\(([-\d.,\s]+)\)\s*\n\s*\),\s*\n\s*limit_ranges", "multi3",
     "起步阶段的 (x),(y),(yaw) 指令区间，当前 ±0.1。"),
    ("指令与课程", "指令上限 limit_ranges", VEL_CFG,
     r"limit_ranges=[\w.]+\.Ranges\(\s*\n\s*lin_vel_x=\(([-\d.,\s]+)\),\s*lin_vel_y=\(([-\d.,\s]+)\),\s*ang_vel_z=\(([-\d.,\s]+)\)", "multi3",
     "课程能达到的最大指令范围。"),
    ("指令与课程", "站立环境占比 rel_standing_envs", VEL_CFG,
     r"rel_standing_envs=([\d.]+)", "raw", "2% 环境给零速度指令。"),

    # ---- domain randomization -------------------------------------------
    ("域随机化", "地面摩擦范围 friction", VEL_CFG,
     r"static_friction_range.*?\(([\d.,\s]+)\)", "tuple", "0.3–1.0。"),
    ("域随机化", "躯干质量附加 (kg)", VEL_CFG,
     r"mass_distribution_params.*?\(([-\d.,\s]+)\)", "tuple", "torso -1~+3kg。"),
    ("域随机化", "推力间隔 push interval (s)", VEL_CFG,
     r'func=mdp\.push_by_setting_velocity,\s*\n\s*mode="interval",\s*\n\s*interval_range_s=\(([\d.,\s]+)\)', "tuple",
     "每 N 秒推一次。"),
    ("域随机化", "推力速度范围 push vel (m/s)", VEL_CFG,
     r'velocity_range":\s*\{"x":\s*\(([-\d.,\s]+)\)', "tuple", "±0.5 m/s。"),

    # ---- terminations ----------------------------------------------------
    ("终止条件", "最小身高 min height (m)", VEL_CFG,
     r'minimum_height":\s*([\d.]+)', "raw", "低于此高度判摔倒。"),
    ("终止条件", "最大倾角 bad_orientation (rad)", VEL_CFG,
     r'limit_angle":\s*([\d.]+)', "raw", "躯干倾角超此值判摔倒。"),

    # ---- PPO -------------------------------------------------------------
    ("PPO 算法", "num_steps_per_env", PPO_CFG,
     r"num_steps_per_env\s*=\s*(\d+)", "raw", "每 env 攒多少步更新一次。"),
    ("PPO 算法", "save_interval (iter)", PPO_CFG,
     r"save_interval\s*=\s*(\d+)", "raw", "每多少 iter 存 checkpoint。"),
    ("PPO 算法", "learning_rate", PPO_CFG,
     r"learning_rate=([\d.eE+-]+)", "raw", "schedule=adaptive 时为初始值。"),
    ("PPO 算法", "clip_param", PPO_CFG,
     r"clip_param=([\d.]+)", "raw", "PPO 裁剪幅度。"),
    ("PPO 算法", "entropy_coef", PPO_CFG,
     r"entropy_coef=([\d.]+)", "raw", "探索熵系数。"),
    ("PPO 算法", "gamma", PPO_CFG,
     r"gamma=([\d.]+)", "raw", "折扣因子。"),
    ("PPO 算法", "lam (GAE)", PPO_CFG,
     r"lam=([\d.]+)", "raw", "GAE lambda。"),
    ("PPO 算法", "desired_kl", PPO_CFG,
     r"desired_kl=([\d.]+)", "raw", "自适应 lr 的目标 KL。"),
    ("PPO 算法", "num_learning_epochs", PPO_CFG,
     r"num_learning_epochs=(\d+)", "raw", "每批经验学几遍。"),
    ("PPO 算法", "num_mini_batches", PPO_CFG,
     r"num_mini_batches=(\d+)", "raw", "每批分几块。"),
    ("PPO 算法", "actor_hidden_dims", PPO_CFG,
     r"actor_hidden_dims=\[([^\]]+)\]", "list", "策略网络宽度。"),
]

# --------------------------------------------------------------------------
# File read/write helpers
# --------------------------------------------------------------------------

def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def knob_get(knob) -> str:
    _, _, path, pattern, fmt, _ = knob
    text = read_file(path)
    m = re.search(pattern, text)
    if not m:
        return "<未匹配>"
    if fmt == "multi3":
        return " | ".join(m.group(i) for i in (1, 2, 3))
    return m.group(1).strip()


def knob_set(knob, new_value: str) -> bool:
    _, label, path, pattern, fmt, _ = knob
    text = read_file(path)
    m = re.search(pattern, text)
    if not m:
        return False
    if fmt == "multi3":
        parts = [p.strip() for p in new_value.split("|")]
        if len(parts) != 3:
            return False
        new_text = text[: m.start()] + m.group(0) + text[m.end():]
        # replace groups inside the matched span one by one (largest first)
        span = m.group(0)
        for i, p in enumerate(parts):
            span = re.sub(re.escape(m.group(i + 1)), p, span, count=1)
        new_text = text[: m.start()] + span + text[m.end():]
    else:
        span = m.group(0)
        val_start = m.start(1) - m.start(0)
        span = span[:val_start] + new_value + span[val_start + len(m.group(1)):]
        new_text = text[: m.start()] + span + text[m.end():]

    bak = path + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8") as f:
            f.write(text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    return True


# --------------------------------------------------------------------------
# Checkpoint / run discovery
# --------------------------------------------------------------------------

def scan_checkpoints() -> list[tuple[str, str, str, str]]:
    """Return list of (display_label, log_root, load_run, checkpoint)."""
    out = []
    for root in (LOGROOT, OLD_LOGROOT):
        for d in sorted(glob.glob(os.path.join(root, "*/"))):
            run = os.path.basename(d.rstrip("/"))
            cks = []
            for f in glob.glob(os.path.join(d, "model_*.pt")):
                ck = os.path.basename(f)
                m = re.match(r"model_(\d+)", ck)
                it = int(m.group(1)) if m else -1
                cks.append((it, ck))
            if cks:
                cks.sort()
                # prefer plain model_N.pt as the "latest" entry; suffixed files
                # like *_logstd.pt are not full policy checkpoints and *_ft.pt
                # staged copies should be offered separately
                plain = [c for c in cks if re.fullmatch(r"model_\d+\.pt", c[1])]
                pool = plain if plain else cks
                it, ck = pool[-1]
                root_tag = "lunarsurface" if "lunarsurface" in root else "velocity"
                label = f"{run} / {ck}  (iter {it}, {len(cks)} ckpts)"
                out.append((f"[{root_tag}] {label}", root, run, ck))
                for it2, ck2 in pool[:-1]:
                    if "_ft" in ck2:
                        out.append((f"[{root_tag}] {run} / {ck2}  (iter {it2})",
                                    root, run, ck2))
    return out


# --------------------------------------------------------------------------
# Log parsing
# --------------------------------------------------------------------------
ITER_RE = re.compile(r"Learning iteration (\d+)/(\d+)")
METRIC_RE = re.compile(r"^\s{2,}([\w/_.]+):\s*(-?[\d.eE+]+)\s*$")

METRICS_OF_INTEREST = [
    "Mean reward",
    "Mean episode length",
    "Episode_Reward/track_lin_vel_xy",
    "Episode_Reward/track_ang_vel_z",
    "Curriculum/terrain_levels",
    "Curriculum/lin_vel_cmd_levels",
    "Metrics/base_velocity/error_vel_xy",
    "Metrics/base_velocity/error_vel_yaw",
    "Episode_Termination/time_out",
    "Episode_Termination/bad_orientation",
]


def parse_log(path: str, max_lines: int | None = None) -> tuple[list[dict], dict]:
    """Parse metric blocks. Returns (history list, last block)."""
    history = []
    cur: dict = {}
    try:
        with open(path, errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return history, {}
    if max_lines:
        lines = lines[-max_lines:]
    for ln in lines:
        mi = ITER_RE.search(ln)
        if mi:
            if cur:
                history.append(cur)
            cur = {"iter": int(mi.group(1)), "target": int(mi.group(2))}
            continue
        mm = METRIC_RE.match(ln)
        if mm and cur:
            try:
                cur[mm.group(1)] = float(mm.group(2))
            except ValueError:
                pass
    if cur:
        history.append(cur)
    return history, (history[-1] if history else {})


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------

class Panel(tk.Tk):
    def __init__(self):
        super().__init__()
        # 2x fonts: double every named font Tk/ttk widgets resolve to.
        # (tk scaling does not reliably resize already-created fonts on X11,
        #  so we set the named fonts' sizes directly; negative sizes are px.)
        for name in ("TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont",
                     "TkHeadingFont", "TkCaptionFont", "TkSmallCaptionFont",
                     "TkIconFont", "TkTooltipFont"):
            try:
                f = tkfont.nametofont(name)
                # fonts here are sized in pixels (negative): -12px -> -32px
                f.configure(size=int(int(f.cget("size")) * 2.7))
            except tk.TclError:
                pass
        ttk.Style(self).configure(".", font="TkDefaultFont")
        self.bold_font = tkfont.Font(font="TkFixedFont", weight="bold")
        self.title("月面 Locomotion 训练控制面板")
        self.geometry("2600x1500")
        self.proc: subprocess.Popen | None = None
        self.proc_name = ""
        self.log_file = tk.StringVar(value=os.path.join(BASE, "g1_panel_train.log"))
        self.knob_vars: dict = {}

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=4, pady=4)
        self.tab_knobs = ttk.Frame(nb)
        self.tab_run = ttk.Frame(nb)
        self.tab_metrics = ttk.Frame(nb)
        nb.add(self.tab_run, text=" 训练控制 ")
        nb.add(self.tab_knobs, text=" 旋钮配置 ")
        nb.add(self.tab_metrics, text=" 实时成果 ")

        self._build_knobs_tab()
        self._build_run_tab()
        self._build_metrics_tab()
        self.after(3000, self._tick)

    # ---------------- knobs tab ------------------------------------------
    def _build_knobs_tab(self):
        top = ttk.Frame(self.tab_knobs)
        top.pack(fill="x", pady=4)
        ttk.Label(top, text="直接读写 cfg 源文件；修改仅对下一次启动生效；首次写入自动存 .bak",
                  foreground="#a60").pack(side="left", padx=6)
        ttk.Button(top, text="重新读取", command=self._load_knobs).pack(side="right", padx=4)
        ttk.Button(top, text="应用全部修改", command=self._apply_knobs).pack(side="right", padx=4)

        canvas = tk.Canvas(self.tab_knobs, highlightthickness=0)
        vsb = ttk.Scrollbar(self.tab_knobs, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-e.delta // 120, "units"))
        self._knob_canvas = inner

        cur_section = None
        sec_frame = None
        for knob in KNOBS:
            section, label, path, pattern, fmt, help_ = knob
            if section != cur_section:
                cur_section = section
                sec_frame = ttk.LabelFrame(self._knob_canvas, text=f" {section} ")
                sec_frame.pack(fill="x", padx=8, pady=6)
            row = ttk.Frame(sec_frame)
            row.pack(fill="x", padx=6, pady=2)
            ttk.Label(row, text=label, width=34, anchor="w").pack(side="left")
            var = tk.StringVar()
            ent = ttk.Entry(row, textvariable=var, width=30)
            ent.pack(side="left", padx=4)
            ttk.Label(row, text=help_, foreground="#777",
                      font="TkDefaultFont").pack(side="left", padx=8)
            self.knob_vars[id(knob)] = (knob, var)
        self._load_knobs()

    def _load_knobs(self):
        for knob, var in self.knob_vars.values():
            var.set(knob_get(knob))

    def _apply_knobs(self):
        fails = []
        for knob, var in self.knob_vars.values():
            if not knob_set(knob, var.get().strip()):
                fails.append(knob[1])
        if fails:
            messagebox.showwarning("部分未写入", "以下旋钮未匹配到文件位置：\n" + "\n".join(fails))
        else:
            messagebox.showinfo("完成", "全部旋钮已写入 cfg 文件（原文件备份为 .bak）")

    # ---------------- run tab --------------------------------------------
    def _build_run_tab(self):
        f = self.tab_run
        cfg = ttk.LabelFrame(f, text=" 运行配置 ")
        cfg.pack(fill="x", padx=8, pady=6)

        r = ttk.Frame(cfg); r.pack(fill="x", padx=6, pady=3)
        ttk.Label(r, text="任务", width=16).pack(side="left")
        self.task_var = tk.StringVar(value=TASK)
        ttk.Combobox(r, textvariable=self.task_var, width=48, state="readonly",
                     values=[TASK, "Unitree-G1-29dof-Velocity"]).pack(side="left")
        ttk.Label(r, text="num_envs").pack(side="left", padx=(12, 2))
        self.nenv_var = tk.StringVar(value="4096")
        ttk.Entry(r, textvariable=self.nenv_var, width=7).pack(side="left")
        ttk.Label(r, text="run_name").pack(side="left", padx=(12, 2))
        self.runname_var = tk.StringVar(value="panel_run")
        ttk.Entry(r, textvariable=self.runname_var, width=18).pack(side="left")

        r = ttk.Frame(cfg); r.pack(fill="x", padx=6, pady=3)
        ttk.Label(r, text="起始断点", width=16).pack(side="left")
        self.ck_var = tk.StringVar()
        self.ck_combo = ttk.Combobox(r, textvariable=self.ck_var, width=95, state="readonly")
        self.ck_combo.pack(side="left")
        ttk.Button(r, text="刷新断点列表", command=self._refresh_ckpts).pack(side="left", padx=6)
        self._ck_map: dict[str, tuple[str, str]] = {}
        self._refresh_ckpts()

        r = ttk.Frame(cfg); r.pack(fill="x", padx=6, pady=3)
        ttk.Label(r, text="新增迭代数", width=16).pack(side="left")
        self.iters_var = tk.StringVar(value="15000")
        ttk.Entry(r, textvariable=self.iters_var, width=10).pack(side="left")
        ttk.Label(r, text="（rsl_rl 的 --max_iterations 是增量：断点 iter + 此值 = 终点）",
                  foreground="#777").pack(side="left", padx=8)
        ttk.Label(r, text="日志文件").pack(side="left", padx=(16, 2))
        ttk.Entry(r, textvariable=self.log_file, width=40).pack(side="left")

        ctrl = ttk.LabelFrame(f, text=" 控制 ")
        ctrl.pack(fill="x", padx=8, pady=6)
        self.btn_start = ttk.Button(ctrl, text="▶ 开始训练", command=self.start_train)
        self.btn_start.pack(side="left", padx=8, pady=8)
        self.btn_stop = ttk.Button(ctrl, text="■ 停止训练", command=self.stop_train, state="disabled")
        self.btn_stop.pack(side="left", padx=8)
        ttk.Button(ctrl, text="▶ 可视化试玩 (play GUI)", command=self.start_play).pack(side="left", padx=8)
        ttk.Label(ctrl, text="试玩 envs").pack(side="left", padx=(2, 2))
        self.play_nenv_var = tk.StringVar(value="4")
        ttk.Entry(ctrl, textvariable=self.play_nenv_var, width=5).pack(side="left")
        self.play_nopush_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="关闭推力干扰", variable=self.play_nopush_var).pack(side="left", padx=(8, 2))
        ttk.Button(ctrl, text="运行三跑 supervisor", command=self.start_supervisor).pack(side="left", padx=8)
        self.status_lbl = ttk.Label(ctrl, text="空闲", foreground="#080")
        self.status_lbl.pack(side="left", padx=20)

        mon = ttk.LabelFrame(f, text=" 进程 / GPU ")
        mon.pack(fill="x", padx=8, pady=6)
        self.proc_txt = tk.Text(mon, height=6, font="TkFixedFont")
        self.proc_txt.pack(fill="x", padx=6, pady=4)

        out = ttk.LabelFrame(f, text=" 训练日志尾部 ")
        out.pack(fill="both", expand=True, padx=8, pady=6)
        self.log_tail = scrolledtext.ScrolledText(out, font="TkFixedFont")
        self.log_tail.pack(fill="both", expand=True, padx=4, pady=4)

    def _refresh_ckpts(self):
        entries = ["（从零开始 / 不加载断点）"]
        self._ck_map = {entries[0]: ("", "", "")}
        for label, root, run, ck in scan_checkpoints():
            entries.append(label)
            self._ck_map[label] = (root, run, ck)
        self.ck_combo.configure(values=entries)
        if not self.ck_var.get():
            self.ck_var.set(entries[0])

    def _train_cmd(self) -> list[str]:
        _root, run, ck = self._ck_map.get(self.ck_var.get(), ("", "", ""))
        args = [f"./unitree_rl_lab.sh -t --task {self.task_var.get()}",
                f"--num_envs {self.nenv_var.get()}",
                f"--run_name {self.runname_var.get()}",
                f"--max_iterations {self.iters_var.get()}"]
        if ck:
            args += ["--resume", f"--load_run {run}", f"--checkpoint {ck}"]
        return args

    def _spawn(self, inner_cmd: str, tag: str):
        if self.proc and self.proc.poll() is None:
            messagebox.showwarning("占用", f"已有进程在跑：{self.proc_name} (pid {self.proc.pid})")
            return
        env = ("PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,"
               "garbage_collection_threshold:0.8 "
               # hybrid laptop GPU (prime-select on-demand): force Isaac Sim GUI
               # onto NVIDIA; without these the RTX renderer inits on the Intel
               # iGPU and segfaults in librtx.scenedb. Harmless when headless.
               "__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia "
               "__VK_LAYER_NV_optimus=NVIDIA_only")
        cmd = (f"{ENV_ACT} && cd {LAB} && "
               f"OMNI_KIT_ACCEPT_EULA=YES {env} {inner_cmd}")
        logf = self.log_file.get()
        self.proc = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=open(logf, "a"), stderr=subprocess.STDOUT,
            preexec_fn=os.setsid)
        self.proc_name = tag
        self.status_lbl.configure(text=f"运行中 {tag} pid={self.proc.pid}", foreground="#c00")
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")

    def start_train(self):
        cmd = " ".join(self._train_cmd()) + f" >> {self.log_file.get()} 2>&1"
        self._spawn(cmd, "train")

    def start_supervisor(self):
        cmd = f"bash {BASE}/run_lunar_surface_3runs_v2.sh >> {BASE}/supervisor_panel.log 2>&1"
        self._spawn(cmd, "supervisor")

    def start_play(self):
        root, run, ck = self._ck_map.get(self.ck_var.get(), ("", "", ""))
        if not ck:
            messagebox.showwarning("需要断点", "可视化试玩需要选择一个 checkpoint")
            return
        # play.py treats --checkpoint as a file PATH (load_run is ignored when
        # checkpoint is set), so pass the absolute checkpoint path.
        ck_path = os.path.join(root, run, ck)
        nopush = "UNITREE_PLAY_NO_PUSH=1 " if self.play_nopush_var.get() else ""
        cmd = (f"{nopush}./unitree_rl_lab.sh -p --task {self.task_var.get()} "
               f"--num_envs {self.play_nenv_var.get()} "
               f"--checkpoint {ck_path} "
               f">> {BASE}/g1_panel_play.log 2>&1")
        self._spawn(cmd, "play")

    def stop_train(self):
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("确认", f"停止 {self.proc_name} (pid {self.proc.pid})？"):
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.status_lbl.configure(text="已发送 SIGTERM", foreground="#a60")
        self.btn_stop.configure(state="disabled")
        self.btn_start.configure(state="normal")

    # ---------------- metrics tab ----------------------------------------
    def _build_metrics_tab(self):
        f = self.tab_metrics
        top = ttk.Frame(f); top.pack(fill="x", padx=6, pady=4)
        ttk.Label(top, text="解析日志：").pack(side="left")
        self.metric_log = tk.StringVar(value=os.path.join(BASE, "g1_lsurface_earth.log"))
        ttk.Entry(top, textvariable=self.metric_log, width=60).pack(side="left", padx=4)
        ttk.Button(top, text="浏览…", command=self._pick_log).pack(side="left")
        ttk.Button(top, text="跟随训练日志", command=lambda: self.metric_log.set(self.log_file.get())).pack(side="left", padx=6)
        ttk.Label(top, text="每 5s 自动刷新", foreground="#777").pack(side="right")

        grid = ttk.LabelFrame(f, text=" 最新指标块 ")
        grid.pack(fill="x", padx=8, pady=4)
        self.metric_lbls = {}
        for i, name in enumerate(METRICS_OF_INTEREST):
            ttk.Label(grid, text=name.split("/")[-1], width=20).grid(
                row=i // 5 * 2, column=i % 5, sticky="w", padx=8, pady=(4, 0))
            lbl = ttk.Label(grid, text="—", font=self.bold_font, width=10)
            lbl.grid(row=i // 5 * 2 + 1, column=i % 5, sticky="w", padx=8, pady=(0, 4))
            self.metric_lbls[name] = lbl

        matplotlib.rcParams.update({"font.size": 14})
        self.fig = Figure(figsize=(14, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=4)

    def _pick_log(self):
        p = filedialog.askopenfilename(initialdir=BASE, title="选训练日志")
        if p:
            self.metric_log.set(p)

    # ---------------- periodic refresh -----------------------------------
    def _tick(self):
        # process status
        lines = []
        if self.proc:
            rc = self.proc.poll()
            lines.append(f"panel 进程: {self.proc_name} pid={self.proc.pid} rc={rc}")
            if rc is not None:
                self.status_lbl.configure(text=f"已退出 rc={rc}", foreground="#080")
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
                self.proc = None
        try:
            gpu = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader"], capture_output=True, text=True, timeout=5).stdout.strip()
            lines.append(f"GPU: {gpu}")
            procs = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory",
                 "--format=csv,noheader"], capture_output=True, text=True, timeout=5).stdout.strip()
            lines.append(f"GPU 进程: {procs or '无'}")
        except Exception as e:
            lines.append(f"nvidia-smi: {e}")
        self.proc_txt.delete("1.0", "end")
        self.proc_txt.insert("1.0", "\n".join(lines))

        # log tail
        lf = self.log_file.get()
        try:
            with open(lf, errors="replace") as fh:
                fh.seek(0, 2)
                size = fh.tell()
                fh.seek(max(0, size - 6000))
                tail = fh.read()
            self.log_tail.delete("1.0", "end")
            self.log_tail.insert("1.0", tail)
            self.log_tail.see("end")
        except OSError:
            pass

        # metrics
        hist, last = parse_log(self.metric_log.get())
        for name, lbl in self.metric_lbls.items():
            lbl.configure(text=f"{last[name]:.4f}" if name in last else "—")
        if hist:
            it = [h["iter"] for h in hist if "iter" in h]
            def series(k):
                return [h.get(k) for h in hist if "iter" in h]
            self.ax.clear()
            r = series("Mean reward")
            self.ax.plot(it, r, label="Mean reward", color="tab:blue", lw=1)
            ax2 = self.ax.twinx()
            ax2.plot(it, series("Episode_Reward/track_lin_vel_xy"),
                     label="track_lin_vel", color="tab:orange", lw=1)
            ax2.plot(it, series("Curriculum/terrain_levels"),
                     label="terrain_level", color="tab:green", lw=1)
            self.ax.set_xlabel("iteration")
            self.ax.set_ylabel("reward")
            ax2.set_ylabel("track / level")
            self.ax.set_title(f"{os.path.basename(self.metric_log.get())}  ({len(hist)} blocks)")
            h1, l1 = self.ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            self.ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8)
            self.ax.grid(alpha=0.3)
            self.canvas_fig.draw_idle()

        self.after(5000, self._tick)


if __name__ == "__main__":
    app = Panel()
    app.mainloop()
