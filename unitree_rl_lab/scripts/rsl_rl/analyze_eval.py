# Offline analyzer for eval_terrain.py output (eval_summary.csv). Pure stdlib,
# CPU-only — run any time, no sim needed.
#
# Turns per-terrain x level aggregates into the roadmap verdicts:
#   - per-terrain fall_rate / mean_rel_err matrices (levels as columns)
#   - "step ceiling": highest stairs-type level with fall_rate <= threshold
#     (level r -> step height in [5+1.5r, 6.5+1.5r) cm; level>=6 == the 15cm gate)
#   - one-line PASS/FAIL per checkpoint against the roadmap gates
#
# Usage:
#   python scripts/rsl_rl/analyze_eval.py <run_dir>/eval/eval_summary.csv
#   python scripts/rsl_rl/analyze_eval.py .../eval_summary.csv \
#       --fall_thresh 0.10 --rel_err_thresh 0.15 --gate_level 6 --min_eps 5

import argparse
import csv
import math
import sys
from collections import defaultdict

parser = argparse.ArgumentParser(description="Analyze eval_summary.csv against roadmap gates.")
parser.add_argument("summary_csv", type=str, help="Path to eval_summary.csv")
parser.add_argument("--fall_thresh", type=float, default=0.10,
                    help="Max fall_rate for a cell to count as 'passable' (default 0.10).")
parser.add_argument("--rel_err_thresh", type=float, default=0.15,
                    help="Max mean_rel_err for the 15cm gate (default 0.15).")
parser.add_argument("--gate_level", type=int, default=6,
                    help="Level at/above which the 15cm-step gate applies (default 6: "
                         "step in [14.0,15.5)cm).")
parser.add_argument("--min_eps", type=int, default=5,
                    help="Cells with fewer episodes are marked '*' and not gate-eligible.")
parser.add_argument("--step_terrains", type=str, default="pyramid_stairs,pyramid_stairs_inv",
                    help="Comma-separated terrain names treated as stairs-type. "
                         "Must match the sub_terrain dict keys reported in the eval log's "
                         "col->name map (training grid: pyramid_stairs/pyramid_stairs_inv; "
                         "heldout grid has no stairs-type terrain).")
args = parser.parse_args()

step_terrains = set(args.step_terrains.split(","))


def step_range_cm(level: int) -> str:
    lo = 5 + 1.5 * level
    return f"[{lo:.1f},{lo + 1.5:.1f})cm"


# checkpoint -> terrain -> level -> row
data = defaultdict(lambda: defaultdict(dict))
ckpt_order = []
terrain_order = []
with open(args.summary_csv, newline="") as f:
    for row in csv.DictReader(f):
        ck, terr, lvl = row["checkpoint"], row["terrain"], int(row["level"])
        if ck not in ckpt_order:
            ckpt_order.append(ck)
        if terr not in terrain_order:
            terrain_order.append(terr)
        rel = row["mean_rel_err"]
        data[ck][terr][lvl] = {
            "eps": int(row["episodes"]),
            "fall": float(row["fall_rate"]),
            "rel": float(rel) if rel not in ("nan", "") else math.nan,
            "len": float(row["mean_ep_len_s"]),
        }

if not ckpt_order:
    sys.exit("empty summary csv")

max_lvl = max(l for ck in data.values() for t in ck.values() for l in t)

for ck in ckpt_order:
    terrs = data[ck]
    print(f"\n=== {ck} ===")
    hdr = "terrain".ljust(20) + "".join(f"L{l:<6}" for l in range(max_lvl + 1))
    print(hdr + "  (fall_rate; *=eps<{}  -=no data)".format(args.min_eps))
    print("-" * len(hdr))
    for terr in terrain_order:
        cells = terrs.get(terr, {})
        line = terr.ljust(20)
        for l in range(max_lvl + 1):
            c = cells.get(l)
            if c is None:
                line += "-      "
            else:
                mark = "*" if c["eps"] < args.min_eps else " "
                line += f"{c['fall']:.2f}{mark}   "[:7]
        print(line)
    print("\nmean_rel_err:")
    for terr in terrain_order:
        cells = terrs.get(terr, {})
        line = terr.ljust(20)
        for l in range(max_lvl + 1):
            c = cells.get(l)
            line += "-      " if c is None or math.isnan(c["rel"]) else f"{c['rel']:.2f}    "[:7]
        print(line)

    # --- step ceiling: contiguous, from L0 up until a stairs level fails ------
    best = None
    for l in range(max_lvl + 1):
        cells = [terrs[t][l] for t in step_terrains if l in terrs.get(t, {})]
        ok = bool(cells) and all(
            c["eps"] >= args.min_eps and c["fall"] <= args.fall_thresh
            and (math.isnan(c["rel"]) or c["rel"] <= args.rel_err_thresh)
            for c in cells)
        if not ok:
            break
        best = l
    # --- 15cm gate: ALL stairs-type cells at level>=gate_level pass ------------
    gate_cells = [(t, l, terrs[t][l]) for t in step_terrains for l in terrs.get(t, {})
                  if l >= args.gate_level]
    thin = [f"{t}@L{l}" for t, l, c in gate_cells if c["eps"] < args.min_eps]
    failing = [f"{t}@L{l}(f={c['fall']:.2f},e={c['rel']:.2f})"
               for t, l, c in gate_cells
               if c["eps"] >= args.min_eps
               and (c["fall"] > args.fall_thresh
                    or (not math.isnan(c["rel"]) and c["rel"] > args.rel_err_thresh))]
    print(f"\nstep ceiling (fall<={args.fall_thresh}, rel<={args.rel_err_thresh}, "
          f"eps>={args.min_eps}): " +
          (f"L{best} -> step {step_range_cm(best)}" if best is not None else "none"))
    if not gate_cells:
        print("15cm gate: NO DATA (no stairs cells)")
    elif failing:
        print(f"15cm gate (all stairs L>={args.gate_level}): FAIL  {', '.join(failing)}")
    elif thin:
        print(f"15cm gate: INCONCLUSIVE (thin cells: {', '.join(thin)})")
    else:
        print("15cm gate: PASS")
