"""Lunar-surface variant of the G1 velocity-tracking task.

Same lunar gravity (1.62 m/s^2) and MDP as ``velocity_env_cfg``, but the ground
is generated from real LRO LOLA DEM crops (NASA GSFC PGDA 5 m/px south-polar
site DEMs) plus procedural micro-relief and craterlets, instead of the flat
cobblestone plane. Difficulty rows map onto increasing mean-slope bands.
"""

import importlib

import isaaclab.terrains as terrain_gen

from unitree_rl_lab.tasks.locomotion.lunar_terrain import LunarDemTerrainCfg

_vel_mod = importlib.import_module("unitree_rl_lab.tasks.locomotion.robots.g1.29dof.velocity_env_cfg")
RobotEnvCfg = _vel_mod.RobotEnvCfg
RobotPlayEnvCfg = _vel_mod.RobotPlayEnvCfg

LUNAR_SURFACE_CFG = terrain_gen.TerrainGeneratorCfg(
    size=(32.0, 32.0),
    border_width=20.0,
    num_rows=9,
    num_cols=10,
    horizontal_scale=0.1,
    vertical_scale=0.005,
    slope_threshold=0.75,
    difficulty_range=(0.0, 1.0),
    use_cache=False,
    seed=42,
    sub_terrains={
        "lunar_dem": LunarDemTerrainCfg(proportion=0.8),
        "flat": terrain_gen.MeshPlaneTerrainCfg(proportion=0.2),
    },
)


class RobotLunarSurfaceEnvCfg(RobotEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_generator = LUNAR_SURFACE_CFG
        self.scene.terrain.max_init_terrain_level = LUNAR_SURFACE_CFG.num_rows - 1
        self.scene.terrain.terrain_generator.curriculum = self.curriculum.terrain_levels is not None
        # DEM meshes are heavier than the flat plane: PhysX asks for >=70MB
        self.sim.physx.gpu_collision_stack_size = 2**26  # keep at scratch-run value: 2**27 OOMs 4096 envs


class RobotLunarSurfacePlayEnvCfg(RobotPlayEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_generator = LUNAR_SURFACE_CFG
        self.scene.terrain.max_init_terrain_level = LUNAR_SURFACE_CFG.num_rows - 1
        self.scene.terrain.terrain_generator.num_rows = 2
        self.scene.terrain.terrain_generator.num_cols = 5
