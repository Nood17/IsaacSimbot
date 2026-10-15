"""Lunar-surface sub-terrain built from real LRO LOLA DEM crops.

Each sub-terrain patch samples a window from a library of real lunar DEM crops
(preprocessed from the NASA GSFC PGDA 5 m/px south-polar site DEMs), scales the
window to the patch size, adds difficulty-scaled micro-relief and small
craterlets, and returns a trimesh. The window is chosen so that its mean slope
increases with the curriculum difficulty parameter.

Generation is deterministic for a fixed ``seed`` (a per-call counter seeds the
RNG), so all training runs generate identical terrain.
"""

from __future__ import annotations

import itertools
import pathlib

import numpy as np
import trimesh
from typing import TYPE_CHECKING

from isaaclab.terrains.sub_terrain_cfg import SubTerrainBaseCfg
from isaaclab.utils import configclass

if TYPE_CHECKING:
    pass

ASSET_DIR = pathlib.Path(__file__).resolve().parents[2] / "assets" / "lunar_dem"

_DEM_CACHE: dict[str, np.ndarray] = {}
_CALL_COUNTER = itertools.count()


def _load_dem(file: str) -> np.ndarray:
    if file not in _DEM_CACHE:
        arr = np.load(ASSET_DIR / file).astype(np.float64)
        _DEM_CACHE[file] = arr
    return _DEM_CACHE[file]


def _grid_mesh(size: tuple[float, float], heights: np.ndarray) -> trimesh.Trimesh:
    """Build a trimesh grid over [0, size[0]] x [0, size[1]] with given heights."""
    n, m = heights.shape
    xs = np.linspace(0.0, size[0], m)
    ys = np.linspace(0.0, size[1], n)
    xx, yy = np.meshgrid(xs, ys)
    vertices = np.column_stack([xx.ravel(), yy.ravel(), heights.ravel()])
    faces = []
    for i in range(n - 1):
        for j in range(m - 1):
            a = i * m + j
            b = a + 1
            c = a + m
            d = c + 1
            faces.append([a, c, b])
            faces.append([b, c, d])
    return trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False)


def _fractal_noise(rng: np.random.Generator, shape: tuple[int, int], cell_px: int) -> np.ndarray:
    """Band-limited noise: sum of upsampled random grids at a few octaves."""
    out = np.zeros(shape)
    amp = 1.0
    total = 0.0
    for k in range(4):
        coarse = rng.standard_normal((shape[0] // cell_px + 2, shape[1] // cell_px + 2))
        yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
        ys = np.linspace(0, coarse.shape[0] - 1, shape[0])
        xs = np.linspace(0, coarse.shape[1] - 1, shape[1])
        yi = np.clip(ys.astype(int), 0, coarse.shape[0] - 2)
        xi = np.clip(xs.astype(int), 0, coarse.shape[1] - 2)
        yf = np.clip(ys - yi, 0, 1)
        xf = np.clip(xs - xi, 0, 1)
        top = coarse[yi[:, None], xi[None, :]] * (1 - xf[None, :]) + coarse[yi[:, None], xi[None, :] + 1] * xf[None, :]
        bot = coarse[yi[:, None] + 1, xi[None, :]] * (1 - xf[None, :]) + coarse[yi[:, None] + 1, xi[None, :] + 1] * xf[None, :]
        out += amp * (top * (1 - yf[:, None]) + bot * yf[:, None])
        total += amp
        amp *= 0.5
        cell_px = max(2, cell_px // 2)
    return out / total


def _add_craters(h: np.ndarray, rng: np.random.Generator, size: float, res: float, count: int) -> None:
    """Stamp simple bowl craters (depth ~ 0.15 * diameter) into the heightmap."""
    n = h.shape[0]
    for _ in range(count):
        d = rng.uniform(0.4, 2.0)          # crater diameter in m
        depth = 0.15 * d
        r = d / 2.0 / res                  # radius in px
        cx = rng.uniform(r, n - r)
        cy = rng.uniform(r, n - r)
        yy, xx = np.mgrid[:n, :n]
        dist = np.hypot(yy - cy, xx - cx) * res
        mask = dist < d
        prof = np.zeros_like(h)
        inside = dist < r
        # bowl: parabolic depression + small rim lip
        prof[inside] += -depth * (1.0 - (dist[inside] / r) ** 2)
        lip = (dist >= r) & mask
        prof[lip] += 0.25 * depth * np.exp(-((dist[lip] - r) / (0.25 * r)) ** 2)
        h += prof


def lunar_dem_terrain(difficulty: float, cfg: "LunarDemTerrainCfg") -> tuple[list[trimesh.Trimesh], np.ndarray]:
    rng = np.random.default_rng(cfg.seed + next(_CALL_COUNTER))

    dem_files = list(cfg.dem_files) if cfg.dem_files else sorted(p.name for p in ASSET_DIR.glob("*.npy"))
    dem = _load_dem(dem_files[rng.integers(len(dem_files))])
    res_dem = cfg.dem_resolution  # m per DEM pixel

    # target mean slope for this difficulty, degrees
    target_slope = cfg.slope_range[0] + (cfg.slope_range[1] - cfg.slope_range[0]) * difficulty
    win_px = max(2, int(round(cfg.size[0] / res_dem)))

    # rejection-sample a window whose mean slope is closest to target
    h_dem, w_dem = dem.shape
    best, best_err = None, np.inf
    for _ in range(cfg.max_tries):
        y = int(rng.integers(0, max(1, h_dem - win_px + 1)))
        x = int(rng.integers(0, max(1, w_dem - win_px + 1)))
        win = dem[y : y + win_px, x : x + win_px]
        if not np.isfinite(win).all():
            continue
        gy, gx = np.gradient(win, res_dem)
        ms = float(np.degrees(np.mean(np.hypot(gx, gy))))
        err = abs(ms - target_slope)
        if err < best_err:
            best, best_err = win, err
        if err < 1.0:
            break
    if best is None:
        best = np.zeros((win_px, win_px))

    # resample DEM window to patch mesh grid
    n = int(round(cfg.size[0] / cfg.horizontal_scale)) + 1
    ys = np.linspace(0, best.shape[0] - 1, n)
    xs = np.linspace(0, best.shape[1] - 1, n)
    yi = np.clip(ys.astype(int), 0, best.shape[0] - 2)
    xi = np.clip(xs.astype(int), 0, best.shape[1] - 2)
    yf = np.clip(ys - yi, 0, 1)
    xf = np.clip(xs - xi, 0, 1)
    h = (
        best[yi[:, None], xi[None, :]] * (1 - yf[:, None]) * (1 - xf[None, :])
        + best[yi[:, None] + 1, xi[None, :]] * yf[:, None] * (1 - xf[None, :])
        + best[yi[:, None], xi[None, :] + 1] * (1 - yf[:, None]) * xf[None, :]
        + best[yi[:, None] + 1, xi[None, :] + 1] * yf[:, None] * xf[None, :]
    )

    # micro-relief: amplitude grows with difficulty (lunar regolith roughness)
    amp = cfg.micro_relief[0] + (cfg.micro_relief[1] - cfg.micro_relief[0]) * difficulty
    if amp > 0:
        h += amp * _fractal_noise(rng, h.shape, cell_px=max(4, n // 8))

    # small craterlets at higher difficulty
    n_craters = int(round(cfg.crater_count[0] + (cfg.crater_count[1] - cfg.crater_count[0]) * difficulty))
    if n_craters > 0:
        _add_craters(h, rng, cfg.size[0], cfg.horizontal_scale, n_craters)

    # normalize so the patch center (robot spawn) sits at z = 0
    h -= h[n // 2, n // 2]

    mesh = _grid_mesh(cfg.size, h)
    origin = np.array([cfg.size[0] / 2.0, cfg.size[1] / 2.0, 0.0])
    return [mesh], origin


@configclass
class LunarDemTerrainCfg(SubTerrainBaseCfg):
    """Sub-terrain that renders real LRO LOLA DEM windows + procedural micro-relief."""

    function = lunar_dem_terrain

    dem_files: tuple[str, ...] = ()
    """Crop files under ``assets/lunar_dem``. Empty = use all ``*.npy`` found there."""

    dem_resolution: float = 5.0
    """Resolution of the DEM data in meters per pixel (LOLA 5mpp products)."""

    horizontal_scale: float = 0.2
    """Mesh vertex spacing inside the patch (m)."""

    slope_range: tuple[float, float] = (0.0, 25.0)
    """Target mean-slope band (deg) mapped onto the difficulty range."""

    micro_relief: tuple[float, float] = (0.0, 0.10)
    """Peak amplitude (m) of procedural micro-relief at difficulty 0 / 1."""

    crater_count: tuple[float, float] = (0.0, 6.0)
    """Number of small craterlets per patch at difficulty 0 / 1."""

    max_tries: int = 200
    """Rejection-sampling budget to match the target slope."""

    seed: int = 42
    """Base seed; combined with a call counter for deterministic generation."""
