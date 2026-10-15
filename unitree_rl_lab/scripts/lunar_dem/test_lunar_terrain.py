#!/usr/bin/env python
"""Standalone sanity test for lunar_terrain.py without booting Isaac Sim.

Stubs the two isaaclab symbols the module needs (SubTerrainBaseCfg, configclass),
then exercises lunar_dem_terrain() at several difficulties and validates the
returned mesh/origin contract used by TerrainGenerator.
"""

import dataclasses
import sys
import types

import numpy as np

# --- stub isaaclab modules ---------------------------------------------------
isaaclab = types.ModuleType("isaaclab")
terrains_pkg = types.ModuleType("isaaclab.terrains")
stc = types.ModuleType("isaaclab.terrains.sub_terrain_cfg")
utils = types.ModuleType("isaaclab.utils")


def configclass(cls):
    return dataclasses.dataclass(cls)


@configclass
class SubTerrainBaseCfg:
    function = None
    proportion: float = 1.0
    size: tuple = (10.0, 10.0)
    flat_patch_sampling: dict | None = None


stc.SubTerrainBaseCfg = SubTerrainBaseCfg
utils.configclass = configclass
sys.modules.update(
    {
        "isaaclab": isaaclab,
        "isaaclab.terrains": terrains_pkg,
        "isaaclab.terrains.sub_terrain_cfg": stc,
        "isaaclab.utils": utils,
    }
)

import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "lunar_terrain",
    "/home/nood/IsaacSimbot/unitree_rl_lab/source/unitree_rl_lab/unitree_rl_lab/tasks/locomotion/lunar_terrain.py",
)
lt = importlib.util.module_from_spec(spec)
sys.modules["lunar_terrain"] = lt
spec.loader.exec_module(lt)
LunarDemTerrainCfg = lt.LunarDemTerrainCfg
lunar_dem_terrain = lt.lunar_dem_terrain

cfg = LunarDemTerrainCfg()
cfg.size = (32.0, 32.0)

print("difficulty | mesh verts | z range (m) | mean slope deg | origin")
for d in [0.0, 0.25, 0.5, 0.75, 1.0]:
    meshes, origin = lunar_dem_terrain(d, cfg)
    m = meshes[0]
    z = m.vertices[:, 2]
    # approximate mean slope of the produced mesh
    n = int(round(cfg.size[0] / cfg.horizontal_scale)) + 1
    h = z.reshape(n, n)
    gy, gx = np.gradient(h, cfg.horizontal_scale)
    ms = np.degrees(np.mean(np.hypot(gx, gy)))
    assert origin.tolist() == [16.0, 16.0, 0.0]
    assert abs(h[n // 2, n // 2]) < 1e-9, "patch center must be z=0"
    assert m.bounds[0][:2].tolist() == [0.0, 0.0] and abs(m.bounds[1][0] - 32.0) < 1e-6
    print(f"{d:9.2f} | {len(m.vertices):10d} | [{z.min():7.2f},{z.max():7.2f}] | {ms:7.2f} | {origin}")

# determinism check: same call sequence -> same terrain

lt._CALL_COUNTER = __import__("itertools").count()
m1, _ = lunar_dem_terrain(0.5, cfg)
lt._CALL_COUNTER = __import__("itertools").count()
m2, _ = lunar_dem_terrain(0.5, cfg)
assert np.allclose(m1[0].vertices, m2[0].vertices), "non-deterministic terrain!"
print("determinism: OK")
