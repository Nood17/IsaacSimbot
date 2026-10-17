# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""A3 teacher-student agent cfgs for Go2 rough terrain (see docs/quadruped/A3-teacher-student实现路径.md).

Stage A (`Unitree-Go2-Velocity-Scan`): plain PPO, but the "policy" obs set reads the
privileged env group "teacher" (proprio + height_scanner) -> the actor IS the teacher.
Stage B (`Unitree-Go2-Velocity-Distill`): DistillationRunner + StudentTeacher;
`--checkpoint <stage-A model_*.pt>` loads the PPO actor weights into the teacher
network automatically (StudentTeacher.load_state_dict renames "actor." keys).
"""

from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import (
    RslRlDistillationAlgorithmCfg,
    RslRlDistillationRunnerCfg,
    RslRlDistillationStudentTeacherCfg,
)

from .rsl_rl_ppo_cfg import BasePPORunnerCfg


@configclass
class Go2ScanPPORunnerCfg(BasePPORunnerCfg):
    """Stage-A teacher runner: PPO actor consumes the scan-augmented `teacher` obs group."""

    # shared experiment dir with the distillation stage: train.py resolves the
    # teacher ckpt as <experiment_name>/<load_run>/<checkpoint>, so both stages
    # must log under the same experiment_name.
    experiment_name = "unitree_go2_velocity_a3"
    obs_groups = {"policy": ["teacher"], "critic": ["critic"]}


@configclass
class Go2DistillationRunnerCfg(RslRlDistillationRunnerCfg):
    """Stage-B runner: distill the scan teacher into a blind (`policy` group) student."""

    num_steps_per_env = 24
    max_iterations = 2000
    save_interval = 100
    experiment_name = "unitree_go2_velocity_a3"
    obs_groups = {"policy": ["policy"], "teacher": ["teacher"]}
    policy = RslRlDistillationStudentTeacherCfg(
        init_noise_std=1.0,
        noise_std_type="scalar",
        # MUST stay False for the teacher: Go2 PPO ckpts contain no *_obs_normalizer.*
        # keys (the pipeline runs Identity normalizers), and StudentTeacher.load_state_dict
        # strict-loads teacher_obs_normalizer -> True would crash on missing keys.
        student_obs_normalization=False,
        teacher_obs_normalization=False,
        student_hidden_dims=[512, 256, 128],
        teacher_hidden_dims=[512, 256, 128],
        activation="elu",
    )
    algorithm = RslRlDistillationAlgorithmCfg(
        num_learning_epochs=5,
        learning_rate=1.0e-3,
        gradient_length=15,
        max_grad_norm=1.0,
    )
