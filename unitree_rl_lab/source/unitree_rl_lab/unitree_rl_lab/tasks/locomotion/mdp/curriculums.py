from __future__ import annotations

import torch
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def lin_vel_cmd_levels(
    env: ManagerBasedRLEnv,
    env_ids: Sequence[int],
    reward_term_name: str = "track_lin_vel_xy",
) -> torch.Tensor:
    command_term = env.command_manager.get_term("base_velocity")
    ranges = command_term.cfg.ranges
    limit_ranges = command_term.cfg.limit_ranges

    # Promotion is evaluated on every reset batch (env_ids just completed full episodes),
    # paced to at most once per episode length. The old `common_step_counter % max_episode_length`
    # gate only fired when a reset coincided with an exact step boundary, so the level never moved.
    if len(env_ids) > 0:
        reward_term = env.reward_manager.get_term_cfg(reward_term_name)
        reward = torch.mean(env.reward_manager._episode_sums[reward_term_name][env_ids]) / env.max_episode_length_s
        last_promote = getattr(env, "_lin_vel_cmd_last_promote", -env.max_episode_length)
        if reward > reward_term.weight * 0.8 and env.common_step_counter - last_promote >= env.max_episode_length:
            env._lin_vel_cmd_last_promote = env.common_step_counter
            delta_command = torch.tensor([-0.1, 0.1], device=env.device)
            ranges.lin_vel_x = torch.clamp(
                torch.tensor(ranges.lin_vel_x, device=env.device) + delta_command,
                limit_ranges.lin_vel_x[0],
                limit_ranges.lin_vel_x[1],
            ).tolist()
            ranges.lin_vel_y = torch.clamp(
                torch.tensor(ranges.lin_vel_y, device=env.device) + delta_command,
                limit_ranges.lin_vel_y[0],
                limit_ranges.lin_vel_y[1],
            ).tolist()

    return torch.tensor(ranges.lin_vel_x[1], device=env.device)


def ang_vel_cmd_levels(
    env: ManagerBasedRLEnv,
    env_ids: Sequence[int],
    reward_term_name: str = "track_ang_vel_z",
) -> torch.Tensor:
    command_term = env.command_manager.get_term("base_velocity")
    ranges = command_term.cfg.ranges
    limit_ranges = command_term.cfg.limit_ranges

    if len(env_ids) > 0:
        reward_term = env.reward_manager.get_term_cfg(reward_term_name)
        reward = torch.mean(env.reward_manager._episode_sums[reward_term_name][env_ids]) / env.max_episode_length_s
        last_promote = getattr(env, "_ang_vel_cmd_last_promote", -env.max_episode_length)
        if reward > reward_term.weight * 0.8 and env.common_step_counter - last_promote >= env.max_episode_length:
            env._ang_vel_cmd_last_promote = env.common_step_counter
            delta_command = torch.tensor([-0.1, 0.1], device=env.device)
            ranges.ang_vel_z = torch.clamp(
                torch.tensor(ranges.ang_vel_z, device=env.device) + delta_command,
                limit_ranges.ang_vel_z[0],
                limit_ranges.ang_vel_z[1],
            ).tolist()

    return torch.tensor(ranges.ang_vel_z[1], device=env.device)
