#!/usr/bin/env python
"""Convert a TensorBoard events file into the rsl_rl console-log text format
that lunar_panel.py parses ("Learning iteration n/m" + indented metric lines).

Usage:
    python events_to_console_log.py <events_file> <output.log>
"""

import sys
from collections import defaultdict

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

# TB tag -> console metric name (names already matching are emitted as-is)
TAG_MAP = {
    "Train/mean_reward": "Mean reward",
    "Train/mean_episode_length": "Mean episode length",
    "Loss/entropy": "Mean entropy loss",
    "Loss/surrogate": "Mean surrogate loss",
    "Loss/value_function": "Mean value_function loss",
    "Loss/learning_rate": "Learn/learning_rate",
    "Policy/mean_noise_std": "Mean action noise std",
}
# tags folded into synthesized lines, or redundant duplicates
SKIP = {"Perf/total_fps", "Perf/collection time", "Perf/learning_time",
        "Train/mean_reward/time", "Train/mean_episode_length/time"}


def main(events_path: str, out_path: str):
    ea = EventAccumulator(events_path)
    ea.Reload()
    tags = ea.Tags()["scalars"]

    series: dict[str, dict[int, float]] = {}
    steps = set()
    for t in tags:
        if t in SKIP:
            continue
        name = TAG_MAP.get(t, t)
        for e in ea.Scalars(t):
            series.setdefault(name, {})[e.step] = e.value
            steps.add(e.step)
    fps = {e.step: e.value for e in ea.Scalars("Perf/total_fps")} if "Perf/total_fps" in tags else {}
    coll = {e.step: e.value for e in ea.Scalars("Perf/collection time")} if "Perf/collection time" in tags else {}
    learn = {e.step: e.value for e in ea.Scalars("Perf/learning_time")} if "Perf/learning_time" in tags else {}

    steps = sorted(steps)
    total = steps[-1] if steps else 0
    with open(out_path, "w", encoding="utf-8") as f:
        for it in steps:
            f.write(f" Learning iteration {it}/{total} \n\n")
            if it in fps:
                f.write(f"                       Computation: {int(fps[it])} steps/s "
                        f"(collection: {coll.get(it, 0):.3f}s, learning {learn.get(it, 0):.3f}s)\n")
            for name in sorted(series):
                v = series[name].get(it)
                if v is not None:
                    f.write(f"        {name}: {v}\n")
            if it in coll or it in learn:
                f.write(f"                    Iteration time: {coll.get(it, 0) + learn.get(it, 0):.2f}s\n")
    print(f"wrote {out_path}: {len(steps)} iterations, {len(series)} metrics")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
