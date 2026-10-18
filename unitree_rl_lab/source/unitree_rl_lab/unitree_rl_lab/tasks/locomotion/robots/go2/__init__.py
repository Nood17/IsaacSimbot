import gymnasium as gym

gym.register(
    id="Unitree-Go2-Velocity-Stairs",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotEnvCfg",
        "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
    },
)


# A1 acceptance env (roadmap stage A1): pre-A2 terrain mix (no stairs) and
# command ranges, for the 3-seed acceptance runs.
gym.register(
    id="Unitree-Go2-Velocity-Rough",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotRoughEnvCfg",
        "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotRoughPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
    },
)

# A3 stage A: teacher PPO (actor reads the privileged `teacher` obs group = proprio + height_scanner)
gym.register(
    id="Unitree-Go2-Velocity-Scan-Stairs",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotScanEnvCfg",
        "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotScanPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_distill_cfg:Go2ScanPPORunnerCfg",
    },
)

# Held-out acceptance env (roadmap discipline #4): terrain types never trained on.
# Agent cfg defaults to BasePPORunnerCfg (blind policies); for teacher/student ckpts
# eval_terrain.py accepts --agent_cfg module:Class to swap the runner cfg.
gym.register(
    id="Unitree-Go2-Velocity-Heldout",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotHeldoutEnvCfg",
        "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotScanPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_ppo_cfg:BasePPORunnerCfg",
    },
)

# A3 stage B: distill the scan teacher into a blind student (`policy` group only)
gym.register(
    id="Unitree-Go2-Velocity-Distill-Stairs",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotScanEnvCfg",
        "play_env_cfg_entry_point": f"{__name__}.velocity_env_cfg:RobotScanPlayEnvCfg",
        "rsl_rl_cfg_entry_point": f"unitree_rl_lab.tasks.locomotion.agents.rsl_rl_distill_cfg:Go2DistillationRunnerCfg",
    },
)
