"""Splice an rsl_rl PPO checkpoint for a larger actor input dim (e.g. +height_scanner).

Warm-start for A3 stage-A teacher training: takes a blind-policy ckpt and produces
one whose `actor.0.weight` accepts `old_in + add_dim` inputs — the new columns are
zero-filled at position `--insert_at` (default: appended at the end; requires the
new obs terms to be declared LAST in the obs group, as in TeacherCfg).

Also pads:
  - actor_obs_normalizer.* buffers if present (mean->0, variance/std->1)
  - optimizer exp_avg/exp_avg_sq tensors whose shape matches the first layer
    (shape-based match; safe because (512, in_dim) is unique in the Go2 ckpts)

Critic / iter / everything else untouched. CPU-only, no sim needed.

Usage:
  python expand_actor_obs.py --in_ckpt <run>/model_8700.pt \
      --out_ckpt ft_init/warm_8700_scan.pt --add_dim 935   # 187 rays * history 5
"""

import argparse
import os

import torch


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in_ckpt", required=True)
    p.add_argument("--out_ckpt", required=True)
    p.add_argument("--add_dim", type=int, required=True, help="New input dims to append (e.g. 187*history).")
    p.add_argument("--insert_at", type=int, default=-1, help="Column index to insert at; -1 = append at end.")
    p.add_argument("--set_iter", type=int, default=None, help="Override ckpt iter (default: keep).")
    args = p.parse_args()

    ck = torch.load(args.in_ckpt, map_location="cpu", weights_only=False)
    sd = ck["model_state_dict"]
    W = sd["actor.0.weight"]
    out_dim, in_dim = W.shape
    at = in_dim if args.insert_at in (-1, in_dim) else args.insert_at
    if not 0 <= at <= in_dim:
        raise ValueError(f"insert_at {args.insert_at} out of range [0, {in_dim}]")

    sd["actor.0.weight"] = torch.cat([W[:, :at], torch.zeros(out_dim, args.add_dim), W[:, at:]], dim=1)
    print(f"[INFO] actor.0.weight: {tuple(W.shape)} -> {tuple(sd['actor.0.weight'].shape)} (insert @{at})")

    for k, v in list(sd.items()):
        if "actor_obs_normalizer" in k and v.ndim >= 1 and v.shape[-1] == in_dim:
            fill = 1.0 if any(s in k for s in ("var", "std", "m2", "count")) else 0.0
            pad = torch.full((*v.shape[:-1], args.add_dim), fill)
            sd[k] = torch.cat([v[..., :at], pad, v[..., at:]], dim=-1)
            print(f"[INFO] padded {k}: {tuple(v.shape)} -> {tuple(sd[k].shape)}")

    for k, v in ck.get("optimizer_state_dict", {}).get("state", {}).items():
        for sk, sv in list(v.items()):
            if torch.is_tensor(sv) and sv.shape == (out_dim, in_dim):
                v[sk] = torch.cat(
                    [sv[:, :at], torch.zeros(out_dim, args.add_dim), sv[:, at:]], dim=1
                )
                print(f"[INFO] optimizer state[{k}].{sk}: {tuple(sv.shape)} -> {tuple(v[sk].shape)}")

    if args.set_iter is not None:
        ck["iter"] = args.set_iter
    os.makedirs(os.path.dirname(os.path.abspath(args.out_ckpt)), exist_ok=True)
    torch.save(ck, args.out_ckpt)
    print(f"[INFO] wrote {args.out_ckpt} (iter={ck.get('iter')})")


if __name__ == "__main__":
    main()
