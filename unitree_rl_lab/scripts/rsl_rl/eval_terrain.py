# Per-terrain evaluation for velocity-tracking policies (roadmap discipline #3/#4).
#
# Loads one or more rsl_rl checkpoints and measures, per sub-terrain type and
# difficulty row:
#   - fall rate (non-timeout termination: bad_orientation / base_contact)
#   - mean absolute velocity-tracking error (m/s) + relative error (err/cmd_speed)
#   - mean episode length
#
# Unlike play.py this uses the *train* env cfg (env_cfg_entry_point) so the full
# num_rows x num_cols terrain grid exists, then freezes the layout:
#   - curriculum.terrain_levels removed -> envs never move cells (clean attribution)
#   - curriculum.lin_vel_cmd_levels removed -> command ranges stay fixed
#   - max_init_terrain_level -> num_rows-1 so every difficulty row is populated
#   - commands.base_velocity.ranges -> limit_ranges (evaluate full cmd distribution)
# TerrainGenerator.curriculum stays True (set in cfg __post_init__ before our
# override), so rows still map linearly onto difficulty_range.
#
# Usage (after training finishes, GPU free; conda env activated):
#   cd unitree_rl_lab
#   python scripts/rsl_rl/eval_terrain.py --task Unitree-Go2-Velocity-Stairs \
#       --headless --num_envs 256 --eval_seconds 300 \
#       --load_run 2026-10-17_18-41-04_A2_stairs_slope_ft --checkpoints "model_*.pt"
#
# Output: <run_dir>/eval/eval_rows.csv (one row per finished episode) and
#         <run_dir>/eval/eval_summary.csv (per terrain x level aggregates).

import argparse
import csv
import glob
import os
import re
from importlib.metadata import version

from isaaclab.app import AppLauncher

import cli_args  # isort: skip

parser = argparse.ArgumentParser(description="Per-terrain evaluation of an rsl_rl velocity policy.")
parser.add_argument("--task", type=str, required=True)
parser.add_argument("--num_envs", type=int, default=256)
parser.add_argument("--eval_seconds", type=float, default=300.0,
                    help="Sim seconds of evaluation per checkpoint.")
parser.add_argument("--checkpoints", type=str, default=None,
                    help="Glob (resolved inside the --load_run dir) or single ckpt filename. "
                         "Default: latest model_*.pt in --load_run.")
parser.add_argument("--min_iter", type=int, default=-1,
                    help="Skip checkpoints with iter < min_iter (when globbing).")
parser.add_argument("--keep_push", action="store_true",
                    help="Keep the push_robot event (default: disabled for clean fall attribution).")
parser.add_argument("--agent_cfg", type=str, default=None,
                    help="Optional 'module:ClassName' to load the rsl_rl agent cfg from, "
                         "overriding the task's rsl_rl_cfg_entry_point (e.g. scan teacher or "
                         "distillation cfgs when evaluating on the Heldout task).")
parser.add_argument("--eval_tag", type=str, default="",
                    help="Suffix appended to eval_rows/eval_summary filenames (e.g. '_heldout') "
                         "so evals on other distributions can share a run dir without clobbering.")
parser.add_argument("--disable_fabric", action="store_true", default=False)
cli_args.add_rsl_rl_args(parser)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import numpy as np
import torch

from rsl_rl.runners import OnPolicyRunner

import isaaclab_tasks  # noqa: F401
from isaaclab.envs import DirectMARLEnv, multi_agent_to_single_agent
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from isaaclab_tasks.utils import get_checkpoint_path

import unitree_rl_lab.tasks  # noqa: F401
from unitree_rl_lab.utils.parser_cfg import parse_env_cfg


def col_to_terrain_names(env) -> dict[int, str]:
    """Map terrain_types (column index) -> sub-terrain name.

    With generator.curriculum=True, columns are assigned deterministically by
    cumulative proportion (see TerrainGenerator curriculum branch).
    """
    gen_cfg = env.unwrapped.scene.terrain.cfg.terrain_generator
    names = list(gen_cfg.sub_terrains.keys())
    props = np.array([c.proportion for c in gen_cfg.sub_terrains.values()], dtype=float)
    props /= props.sum()
    cumsum = np.cumsum(props)
    out = {}
    for col in range(gen_cfg.num_cols):
        idx = int(np.min(np.where(col / gen_cfg.num_cols + 0.001 < cumsum)[0]))
        out[col] = names[idx]
    return out


def resolve_checkpoints(log_root: str, agent_cfg) -> list[str]:
    if args_cli.checkpoint and not args_cli.checkpoints:
        return [os.path.join(log_root, agent_cfg.load_run, args_cli.checkpoint)]
    run_dir = os.path.join(log_root, agent_cfg.load_run)
    if args_cli.checkpoints:
        pattern = os.path.join(run_dir, args_cli.checkpoints)
        files = sorted(glob.glob(pattern))
    else:
        files = sorted(glob.glob(os.path.join(run_dir, "model_*.pt")))
    def it_of(p):
        m = re.search(r"model_(\d+)\.pt$", os.path.basename(p))
        return int(m.group(1)) if m else -1
    files = [f for f in files if it_of(f) >= args_cli.min_iter]
    files.sort(key=it_of)
    if not files:
        # fall back to IsaacLab's resolver (latest)
        files = [get_checkpoint_path(log_root, agent_cfg.load_run, agent_cfg.load_checkpoint)]
    return files


def main():
    env_cfg = parse_env_cfg(
        args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
        entry_point_key="env_cfg_entry_point",
    )

    # --- freeze the terrain layout for clean per-cell attribution -------------
    env_cfg.curriculum.terrain_levels = None
    env_cfg.curriculum.lin_vel_cmd_levels = None
    gen_cfg = env_cfg.scene.terrain.terrain_generator
    if gen_cfg is not None:
        env_cfg.scene.terrain.max_init_terrain_level = gen_cfg.num_rows - 1
    env_cfg.commands.base_velocity.ranges = env_cfg.commands.base_velocity.limit_ranges
    if not args_cli.keep_push and hasattr(env_cfg.events, "push_robot"):
        env_cfg.events.push_robot = None

    if args_cli.agent_cfg:
        import importlib

        module_name, class_name = args_cli.agent_cfg.split(":")
        agent_cfg = getattr(importlib.import_module(module_name), class_name)()
        agent_cfg = cli_args.update_rsl_rl_cfg(agent_cfg, args_cli)
    else:
        agent_cfg = cli_args.parse_rsl_rl_cfg(args_cli.task, args_cli)
    # --experiment_name is declared in cli_args but never applied to the cfg; honor
    # it here so e.g. Heldout evals can point --load_run at unitree_go2_velocity runs.
    experiment_name = args_cli.experiment_name or agent_cfg.experiment_name
    log_root = os.path.abspath(os.path.join("logs", "rsl_rl", experiment_name))
    ckpts = resolve_checkpoints(log_root, agent_cfg)
    print(f"[INFO] Evaluating {len(ckpts)} checkpoint(s): {[os.path.basename(c) for c in ckpts]}")

    env = gym.make(args_cli.task, cfg=env_cfg)
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)
    env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    if not hasattr(agent_cfg, "class_name") or agent_cfg.class_name == "OnPolicyRunner":
        runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    elif agent_cfg.class_name == "DistillationRunner":
        from rsl_rl.runners import DistillationRunner

        runner = DistillationRunner(env, agent_cfg.to_dict(), log_dir=None, device=agent_cfg.device)
    else:
        raise ValueError(f"Unsupported runner class: {agent_cfg.class_name}")

    terrain = env.unwrapped.scene.terrain
    col2name = col_to_terrain_names(env)
    levels = terrain.terrain_levels.clone()
    types = terrain.terrain_types.clone()
    num_rows = gen_cfg.num_rows if gen_cfg is not None else int(levels.max().item()) + 1
    print(f"[INFO] Terrain grid {num_rows} rows x {len(col2name)} cols; col->name: {col2name}")

    # snapshot per-term dones inside compute() (rows are cleared on env reset)
    tm = env.unwrapped.termination_manager
    term_names = list(tm.active_terms)
    snap = {"term_dones": None}
    orig_compute = tm.compute

    def hooked_compute():
        r = orig_compute()
        snap["term_dones"] = tm._term_dones.clone()
        return r

    tm.compute = hooked_compute

    cmd_term = env.unwrapped.command_manager.get_term("base_velocity")
    robot = env.unwrapped.scene["robot"]
    device = env.unwrapped.device
    n = env.unwrapped.num_envs
    dt = env.unwrapped.step_dt
    max_steps = int(args_cli.eval_seconds / dt)

    run_dir = os.path.dirname(ckpts[0])
    eval_dir = os.path.join(run_dir, "eval")
    os.makedirs(eval_dir, exist_ok=True)
    rows_path = os.path.join(eval_dir, f"eval_rows{args_cli.eval_tag}.csv")
    new_file = not os.path.exists(rows_path)
    rows_f = open(rows_path, "a", newline="")
    writer = csv.writer(rows_f)
    if new_file:
        writer.writerow([
            "checkpoint", "iter", "env_id", "terrain", "col", "level", "difficulty",
            "cause", "ep_len_s", "err_xy_mps", "err_yaw_rads", "cmd_speed_mps",
        ])

    obs = env.get_observations()
    if version("rsl-rl-lib").startswith("2.3."):
        obs, _ = env.get_observations()

    all_rows = []
    for ckpt in ckpts:
        m = re.search(r"model_(\d+)\.pt$", os.path.basename(ckpt))
        it = int(m.group(1)) if m else -1
        runner.load(ckpt, load_optimizer=False)
        policy = runner.get_inference_policy(device=device)
        obs, _ = env.reset()  # clean boundary: don't attribute mid-flight episodes to the new ckpt

        # per-env accumulators
        ep_len = torch.zeros(n, device=device)
        err_xy_sum = torch.zeros(n, device=device)
        err_yaw_sum = torch.zeros(n, device=device)
        cmd_sp_sum = torch.zeros(n, device=device)
        ep_rows = []

        warned = False
        for step in range(max_steps):
            with torch.inference_mode():
                actions = policy(obs)
                obs, _, dones, extras = env.step(actions)

            cmd = cmd_term.command  # (N,3) commanded vx,vy,yawrate in base frame
            err_xy = torch.norm(cmd[:, :2] - robot.data.root_lin_vel_b[:, :2], dim=-1)
            err_yaw = torch.abs(cmd[:, 2] - robot.data.root_ang_vel_b[:, 2])
            cmd_sp = torch.norm(cmd[:, :2], dim=-1)
            err_xy_sum += err_xy
            err_yaw_sum += err_yaw
            cmd_sp_sum += cmd_sp
            ep_len += 1.0

            done_ids = dones.nonzero(as_tuple=False).squeeze(-1)
            if len(done_ids) > 0:
                time_outs = extras.get("time_outs")
                td = snap["term_dones"]
                if td is None and not warned:
                    print("[WARN] termination snapshot unavailable; causes will be timeout/fall only")
                    warned = True
                for e in done_ids.tolist():
                    cause = "unknown"
                    if td is not None and td[e].any():
                        idx = int(td[e].nonzero(as_tuple=False)[0].item())
                        cause = term_names[idx] if idx < len(term_names) else f"term{idx}"
                    elif time_outs is not None and bool(time_outs[e]):
                        cause = "time_out"
                    steps = max(ep_len[e].item(), 1.0)
                    level = int(levels[e].item())
                    col = int(types[e].item())
                    ep_rows.append({
                        "checkpoint": os.path.basename(ckpt), "iter": it, "env_id": e,
                        "terrain": col2name.get(col, f"col{col}"), "col": col, "level": level,
                        # generator: difficulty = (row + U(0,1)) / num_rows -> E[d] = (level+0.5)/num_rows
                        "difficulty": (level + 0.5) / max(num_rows, 1),
                        "cause": cause, "ep_len_s": steps * dt,
                        "err_xy_mps": err_xy_sum[e].item() / steps,
                        "err_yaw_rads": err_yaw_sum[e].item() / steps,
                        "cmd_speed_mps": cmd_sp_sum[e].item() / steps,
                    })
                    ep_len[e] = 0.0
                    err_xy_sum[e] = 0.0
                    err_yaw_sum[e] = 0.0
                    cmd_sp_sum[e] = 0.0

            if (step + 1) % int(60 / dt) == 0:
                print(f"[INFO] {os.path.basename(ckpt)}: {(step + 1) * dt:.0f}s / "
                      f"{args_cli.eval_seconds:.0f}s, {len(ep_rows)} episodes done")

        for r in ep_rows:
            writer.writerow([r[k] for k in ["checkpoint", "iter", "env_id", "terrain", "col",
                                          "level", "difficulty", "cause", "ep_len_s",
                                          "err_xy_mps", "err_yaw_rads", "cmd_speed_mps"]])
        rows_f.flush()
        all_rows.extend(ep_rows)
        print(f"[INFO] {os.path.basename(ckpt)}: {len(ep_rows)} episodes collected")

    rows_f.close()

    # --- aggregate ------------------------------------------------------------
    sum_path = os.path.join(eval_dir, f"eval_summary{args_cli.eval_tag}.csv")
    groups = {}
    for r in all_rows:
        groups.setdefault((r["checkpoint"], r["terrain"], r["level"]), []).append(r)
    with open(sum_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["checkpoint", "terrain", "level", "difficulty", "episodes",
                    "fall_rate", "timeout_rate", "mean_err_xy_mps", "mean_rel_err",
                    "mean_ep_len_s"])
        for (ck, terr, lvl), rs in sorted(groups.items(), key=lambda x: (x[0][1], x[0][2])):
            eps = len(rs)
            falls = sum(1 for r in rs if r["cause"] not in ("time_out", "unknown"))
            timeouts = sum(1 for r in rs if r["cause"] == "time_out")
            m_err = np.mean([r["err_xy_mps"] for r in rs])
            rel = [r["err_xy_mps"] / r["cmd_speed_mps"] for r in rs if r["cmd_speed_mps"] > 0.05]
            m_rel = float(np.mean(rel)) if rel else float("nan")
            m_len = np.mean([r["ep_len_s"] for r in rs])
            w.writerow([ck, terr, lvl, round((lvl + 0.5) / num_rows, 3), eps,
                        round(falls / eps, 4), round(timeouts / eps, 4),
                        round(m_err, 4), round(m_rel, 4), round(m_len, 2)])
    print(f"[INFO] Wrote {rows_path}\n[INFO] Wrote {sum_path}")

    env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
