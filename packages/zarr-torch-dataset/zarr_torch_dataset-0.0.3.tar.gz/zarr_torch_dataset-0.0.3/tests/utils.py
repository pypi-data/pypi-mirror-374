import logging.config
import typing
from pathlib import Path

import numpy as np
import zarr

from zarrdataset import ZarrDataLoader, ZarrIterableDataset

DATASET_PATH = Path('tmp.zarr')


def create_dataset():
    nb_case = 1_000
    nb_vars = 4
    x_res = 1024
    y_res = 720
    chunks_size = 100
    data = np.arange(nb_case*nb_vars*x_res*y_res).reshape((nb_case, nb_vars, x_res, y_res))
    with zarr.storage.LocalStore(DATASET_PATH) as store:  # type: ignore
        samples = zarr.create_array(store=store, shape=data.shape, dtype=np.float32,
                                    chunks=(chunks_size, nb_vars, x_res, y_res), compressors=None)
        samples[:] = data


def open_dataset() -> tuple[zarr.Array, np.ndarray]:
    samples = zarr.open(store=DATASET_PATH)
    samples = typing.cast(zarr.Array, samples)
    return samples, np.arange(samples.shape[0])


def create_dataloader(samples: zarr.Array,
                      targets: zarr.Array | np.ndarray | None,
                      num_workers: int,
                      batch_size: int,
                      prefetch_factor: int,
                      drop_last: bool
                      ) -> ZarrDataLoader:
    ds = ZarrIterableDataset(samples=samples,
                             targets=targets,
                             shuffle_chunks=True,
                             chunks_shuffle_seed=1,
                             shuffle_buffer=True,
                             buffer_shuffle_seed=2)
    if num_workers >= 1:
        da = ZarrDataLoader(dataset=ds,
                            num_workers=num_workers,
                            batch_size=batch_size,
                            multiprocessing_context='fork',
                            pin_memory=True,
                            prefetch_factor=prefetch_factor,
                            drop_last=drop_last)
    else:
        da = ZarrDataLoader(dataset=ds, num_workers=num_workers,
                            batch_size=batch_size, drop_last=drop_last)
    return da


def display_duration(time_in_sec: float) -> str:
    remainder = time_in_sec % 60
    if remainder == time_in_sec:
        return f'{time_in_sec:.2f} seconds'
    else:
        seconds = remainder
        minutes = int(time_in_sec / 60)
        remainder = minutes % 60
        if remainder == minutes:
            return f'{minutes} mins, {seconds:.2f} seconds ({time_in_sec:.2f} s)'
        else:
            hours   = int(minutes / 60)
            minutes = remainder
            remainder = hours % 24
            if remainder == hours:
                return f'{hours} hours, {minutes} mins, {seconds:.2f} seconds ({time_in_sec:.2f} s)'
            else:
                days = int(hours / 24)
                hours = remainder
                return f'{days} days, {hours} hours, {minutes} mins, {seconds:.2f} seconds ({time_in_sec:.2f} s)'


def set_logging_config() -> None:
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'zarrdataset_formatter': {
                'format': '%(message)s',
            },
        },
        'handlers': {
            'zarrdataset_stdout': {
                'class': 'logging.StreamHandler',
                'formatter': 'zarrdataset_formatter',
                'stream': 'ext://sys.stdout'
            },
        },
        'loggers': {
            'zarrdataset': {
                'handlers': ['zarrdataset_stdout'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    }
    logging.config.dictConfig(logging_config)
