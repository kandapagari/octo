from copy import deepcopy

from config import get_config as get_base_config
from config import update_config

get_base_config = get_base_config.__wrapped__


def get_config():
    base_config = get_base_config("dummy")
    del base_config["dataset_kwargs"]["oxe_kwargs"]
    config = update_config(
        base_config,
        num_steps=2,
        optimizer=dict(
            learning_rate=dict(
                warmup_steps=1,
            ),
        ),
        batch_size=64,
        shuffle_buffer_size=1000,
        num_val_batches=1,
        log_interval=1,
        eval_interval=2,
        eval_datasets=None,
        trajs_for_metrics=1,
        trajs_for_viz=1,
        dataset_kwargs={
            "dataset_kwargs_list": [
                {
                    "name": "bridge_dataset",
                    "data_dir": "./tests/debug_dataset",
                    "image_obs_keys": ["image_0"],
                    "state_obs_keys": ["state"],
                },
            ],
            "traj_transform_threads": 1,  # shared between all datasets
            "traj_read_threads": 1,  # shared between all datasets
            "frame_transform_threads": 4,  # not shared between datasets
        },
    )
    return config
