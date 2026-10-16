#!/usr/bin/env python
"""Preprocess LRO LOLA 5 m/px site DEMs (PGDA) into numpy crops for terrain generation.

Reads the GeoTIFFs in ``lunar_assets/`` (site-level south-polar stereographic DEMs,
pixel values = surface height in meters) and writes a library of fixed-size crops
to ``source/unitree_rl_lab/unitree_rl_lab/assets/lunar_dem/``.

Usage (env_isaaclab python):
    python scripts/lunar_dem/prepare_dem_crops.py
"""

from __future__ import annotations

import json
import pathlib

import numpy as np
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parents[2]
SRC_DIR = pathlib.Path("/home/ubuntu/nood/lunar_assets")
OUT_DIR = REPO / "source/unitree_rl_lab/unitree_rl_lab/assets/lunar_dem"

DEM_RES = 5.0          # meters per pixel (LOLA 5mpp products)
CROP_PX = 64           # crop edge in pixels -> 320 m x 320 m
STRIDE_PX = 32         # sliding window stride
MIN_VALID_FRAC = 0.95  # drop crops with too many nodata pixels


def load_dem(path: pathlib.Path) -> np.ndarray:
    img = Image.open(path)
    dem = np.array(img, dtype=np.float32)
    # LOLA rasters may use a large negative nodata value; mask as NaN
    dem[dem < -1e4] = np.nan
    return dem


def mean_slope_deg(dem: np.ndarray, res: float = DEM_RES) -> float:
    gy, gx = np.gradient(dem, res)
    return float(np.degrees(np.nanmean(np.hypot(gx, gy))))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta: list[dict] = []

    for tif in sorted(SRC_DIR.glob("Site*_surf.tif")):
        site = tif.stem.split("_")[0]
        dem = load_dem(tif)
        h, w = dem.shape
        print(f"{site}: {w}x{h} px, elev range [{np.nanmin(dem):.1f}, {np.nanmax(dem):.1f}] m")

        crops = []
        for y in range(0, h - CROP_PX + 1, STRIDE_PX):
            for x in range(0, w - CROP_PX + 1, STRIDE_PX):
                c = dem[y : y + CROP_PX, x : x + CROP_PX]
                if np.isfinite(c).mean() < MIN_VALID_FRAC:
                    continue
                crops.append((mean_slope_deg(c), x, y, c))
        if not crops:
            print(f"  no valid crops for {site}, skipped")
            continue

        # sort by slope and keep ~16 crops spread over the slope quantiles + random mid ones
        crops.sort(key=lambda t: t[0])
        n = len(crops)
        idxs = np.unique(
            np.concatenate(
                [
                    np.linspace(0, n - 1, 8).astype(int),          # quantile sweep
                    np.random.default_rng(0).integers(0, n, 8),    # random filler
                ]
            )
        )
        kept = [crops[i] for i in idxs]
        for i, (slope, x, y, c) in enumerate(kept):
            name = f"{site}_crop{i:02d}.npy"
            np.save(OUT_DIR / name, c)
            meta.append(
                {"file": name, "site": site, "x": int(x), "y": int(y), "mean_slope_deg": round(slope, 3)}
            )
        print(f"  kept {len(kept)} crops, slopes {[round(k[0],1) for k in kept]} deg")

    with open(OUT_DIR / "meta.json", "w") as f:
        json.dump(
            {
                "source": "NASA GSFC PGDA LOLA 5mpp south-polar site DEMs "
                "(https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/)",
                "resolution_m_per_px": DEM_RES,
                "crop_px": CROP_PX,
                "crop_m": CROP_PX * DEM_RES,
                "units": "meters",
                "reference": "Barker et al. 2021, PSS 203, doi:10.1016/j.pss.2020.105119",
                "crops": meta,
            },
            f,
            indent=2,
        )
    print(f"wrote {len(meta)} crops to {OUT_DIR}")


if __name__ == "__main__":
    main()
