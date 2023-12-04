#!/usr/bin/env python3

import os

from absl import app, flags, logging
import numpy as np

from orca.utils.run_eval import run_eval_loop

from widowx_envs.widowx_env_service import WidowXClient, WidowXConfigs, WidowXStatus
from widowx_wrapper import convert_obs, state_to_eep, wait_for_obs, WidowXGym

np.set_printoptions(suppress=True)

logging.set_verbosity(logging.WARNING)

FLAGS = flags.FLAGS

# custom to bridge_data_robot
flags.DEFINE_string("ip", "localhost", "IP address of the robot")
flags.DEFINE_integer("port", 5556, "Port of the robot")
flags.DEFINE_spaceseplist("goal_eep", [0.3, 0.0, 0.15], "Goal position")
flags.DEFINE_spaceseplist("initial_eep", [0.3, 0.0, 0.15], "Initial position")
flags.DEFINE_bool("blocking", False, "Use the blocking controller")

# enable envlogger
flags.DEFINE_bool("enable_envlogger", False, "Enable envlogger")

##############################################################################

STEP_DURATION_MESSAGE = """
Bridge data was collected with non-blocking control and a step duration of 0.2s.
However, we relabel the actions to make it look like the data was collected with
blocking control and we evaluate with blocking control.
We also use a step duration of 0.4s to reduce the jerkiness of the policy.
Be sure to change the step duration back to 0.2 if evaluating with non-blocking control.
"""
STEP_DURATION = 0.4
STICKY_GRIPPER_NUM_STEPS = 1
WORKSPACE_BOUNDS = [[0.1, -0.15, -0.01, -1.57, 0], [0.45, 0.25, 0.25, 1.57, 0]]
CAMERA_TOPICS = [{"name": "/blue/image_raw"}]
ENV_PARAMS = {
    "camera_topics": CAMERA_TOPICS,
    "override_workspace_boundaries": WORKSPACE_BOUNDS,
    "move_duration": STEP_DURATION,
}

##############################################################################



def main(_):
    # set up the widowx client
    if FLAGS.initial_eep is not None:
        assert isinstance(FLAGS.initial_eep, list)
        initial_eep = [float(e) for e in FLAGS.initial_eep]
        start_state = np.concatenate([initial_eep, [0, 0, 0, 1]])
    else:
        start_state = None

    env_params = WidowXConfigs.DefaultEnvParams.copy()
    env_params.update(ENV_PARAMS)
    env_params["state_state"] = list(start_state)
    widowx_client = WidowXClient(host=FLAGS.ip, port=FLAGS.port)
    widowx_client.init(env_params, image_size=FLAGS.im_size)
    env = WidowXGym(
        widowx_client, FLAGS.im_size, FLAGS.blocking, STICKY_GRIPPER_NUM_STEPS
    )

    if not FLAGS.blocking:
        assert STEP_DURATION == 0.2, STEP_DURATION_MESSAGE

    def custom_goal_condition_init():
        assert isinstance(FLAGS.goal_eep, list)
        _eep = [float(e) for e in FLAGS.goal_eep]
        goal_eep = state_to_eep(_eep, 0)
        widowx_client.move_gripper(1.0)  # open gripper

        move_status = None
        while move_status != WidowXStatus.SUCCESS:
            move_status = widowx_client.move(goal_eep, duration=1.5)

        input("Press [Enter] when ready for taking the goal image. ")
        obs = wait_for_obs(widowx_client)
        return convert_obs(obs, FLAGS.im_size)

    # this logs the env data
    if FLAGS.enable_envlogger:
        from oxe_envlogger.envlogger import OXEEnvLogger
        env = OXEEnvLogger(
            env,
            "widowx",
            directory=os.path.expanduser("~/logs"),
            max_episodes_per_file=100,
        )

    # run the evaluation loop
    run_eval_loop(env, custom_goal_condition_init, STEP_DURATION)
    del env


if __name__ == "__main__":
    app.run(main)
