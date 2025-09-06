import ast
import logging
import re
import typing
from dataclasses import dataclass
from io import StringIO

import numpy as np
import numpy.typing
import pandas as pd
import pytest
import zarr

import tests.utils
from zarrdataset import ZarrDataLoader, ZarrIterableDataset

####################################################################################################

# 1. Can't get logging messages when spawning workers: fork is the only method to get the messages.
# 2. Generally caplog is used to capture log messages, but it doesn't work when forking (and
#    spawning) workers (issue: https://github.com/pytest-dev/pytest/issues/12116).
#    So capfd thought logging configuration in utils.py is the a solution.
# 3. Pytest must execute the tests without capture, i.e.: add -s flag.
# 4. Some examples:
#    - uv run pytest -s --cov -n 5 tests/test_it_ds.py
#    - uv run pytest -s -n 5 "tests/test_it_ds.py::test_multi_processes"
#    - uv run pytest -s "tests/test_it_ds.py::test_multi_processes[10-2-2-2-5]"
#    - uv run pytest -s "tests/test_it_ds.py::test_single_process"
#    - uv run pytest -s "tests/test_it_ds.py::test_target_as_zarr"
#    - uv run pytest -s "tests/test_it_ds.py::test_target_as_pandas_series"
#    - uv run pytest -s "tests/test_it_ds.py::test_chunk_indexes"

####################################################################################################

_LOG_KEY_PATTERN: typing.Pattern = re.compile('\\[\\w+\\]')

tests.utils.set_logging_config()

_LOGGER = logging.getLogger("zarrdataset")


@dataclass
class ChunkIndexParams:
    samples: zarr.Array
    expected_sequence: numpy.typing.NDArray[np.integer]
    selected_chunk_indexes: int | typing.Sequence | numpy.typing.NDArray[np.integer]
    expected_chunk_indexes: typing.Sequence


def create_zarr_array(chunk_size: int) -> zarr.Array:
    with zarr.storage.MemoryStore() as store: # type: ignore
        data = np.arange(500)
        z = zarr.create_array(store=store, shape=data.shape, dtype=np.int32,
                              chunks=(chunk_size,), compressors=None)
        z[:] = data
        return z


@pytest.fixture(scope='module', params=[10, 11])
def samples(request) -> zarr.Array:
    return create_zarr_array(request.param)


@pytest.fixture(scope='module')
def targets(samples) -> np.ndarray:
    return np.arange(samples.shape[0])


@pytest.fixture(params=[1, 2, 3, 5])
def max_epochs(request) -> typing.Generator:
    return request.param


@pytest.fixture(params=[1, 2, 3, 5])
def num_workers(request) -> typing.Generator:
    return request.param


@pytest.fixture(params=[1, 2, 3, 5])
def prefetch_factor(request) -> typing.Generator:
    return request.param


@pytest.fixture(params=[5, 9, 10, 15, 19, 20, 23])
def batch_size(request) -> typing.Generator:
    return request.param


def _core_test(da: ZarrDataLoader,
               max_epochs: int,
               samples: zarr.Array,
               is_shuffled: bool,
               capfd) -> None:
    all_sample_batches = list()
    for epoch in range(0, max_epochs):
        _LOGGER.debug(f'[TEST][EPOCH] = {epoch}')
        sample_batches = list()
        for batch in da:
            sample_batches.append(batch[0])
            all_sample_batches.append(batch[0])
            # Check sample and target batch equality.
            assert np.array_equal(batch[0], batch[1]), 'failed sample batch and target batch equality'
        if is_shuffled:
            batch_elements = np.concatenate(sample_batches, axis=0)
            batch_elements.sort(axis=0)
        else:
            # Batches must be ordered according to their first element, as
            # in multiprocessing context, batches are given randomly.
            sample_batches = sorted(sample_batches, key=lambda x: x[0])
            batch_elements = np.concatenate(sample_batches, axis=0)
        # Check samples and sample batches equality.
        assert np.array_equal(typing.cast(np.ndarray, samples), batch_elements), \
               'failed samples and samples batches equality'
    captured = capfd.readouterr()
    # Check uniqueness of the sample buffers.
    for index in range(0, len(all_sample_batches)-1):
        assert not np.array_equal(all_sample_batches[index], all_sample_batches[index+1]), \
                'failed sample batch uniqueness'
    #assert False, f'\n{str(captured.out)}'  # DEBUG
    _check(captured.out, is_shuffled)
    #assert False, f'\n{str(captured.out)}'  # DEBUG


def _create_log_records(stream: str) -> dict:
    result: dict = dict()
    buffer = StringIO(stream)
    for line in buffer.readlines():
        line = line.removesuffix("\n")
        if '[TEST]' in line:
            step_key = ast.literal_eval(line.split('=')[1])
            result[step_key] = dict()
            step = result[step_key]
        else:
            splits = line.split('=')
            keys = _LOG_KEY_PATTERN.findall(splits[0])
            previous_step = step  # type: ignore
            for index in range(0, len(keys)):
                key = keys[index][1:-1]
                if index < len(keys)-1:
                    previous_step = previous_step.setdefault(key, dict())
                else:
                    value = line.split('=')[1]
                    value = ast.literal_eval(value)
                    previous_step[key] = value
    return result


def _check_shuffling(array: typing.Sequence, threshold: float) -> bool:
    differences = np.diff(array)
    nb_successive = np.sum(differences == 1)
    nb_total = len(differences)
    ratio = nb_successive / nb_total
    return ratio < threshold


def _check_same_arrays(arrays: typing.Sequence[typing.Sequence]) -> bool:
    first_array = arrays[0]
    for array in arrays[1:]:
        if array != first_array:
            return False
    return True


def _check(stream: str, is_shuffled: bool) -> None:
    # Check if -s flag was given to pytest.
    assert stream, 'missing pytest -s flag'
    log_records = _create_log_records(stream)
    sample_buffer_indexes_list = list()

    for epoch in log_records.keys():
        # Check if -s flag was given to pytest.
        assert log_records[epoch].values(), 'missing pytest -s flag'
        process = log_records[epoch]['R0']
        for worker_id in process.keys():
            worker_node = process[worker_id]
            sample_buffer_indexes = worker_node['IT']['BUFFER']['SAMPLE_INDEXES']
            if is_shuffled:
                assert _check_shuffling(sample_buffer_indexes, 0.3), 'failed sample buffer indexes ' + \
                                                                     'shuffle quality'
            sample_buffer_indexes_list.append(sample_buffer_indexes)

        if epoch == 0:
            permutations = list()
            chunk_partitions = list()

            for worker_id in process.keys():
                worker_node = process[worker_id]
                chunk_partition = worker_node['DS']['CHUNKS_PARTITION']['FINAL']
                chunk_partitions.append(chunk_partition)
                # Check partition shuffling.
                if len(chunk_partition) > 1 and is_shuffled:
                    assert _check_shuffling(chunk_partition, 0.5), 'failed chunk partition shuffle quality'
                permutations.append(worker_node['DS']['PERMUTATION'])

            # Check permutations equality across workers.
            if len(permutations) > 1:
                assert _check_same_arrays(permutations), 'failed permutation equality across workers'

            # Check chunk partitions overlapping.
            chunk_indexes = np.concatenate(chunk_partitions)
            unique, counts = np.unique(chunk_indexes, return_counts=True)  # unique is sorted.
            assert counts.max() == 1, 'failed chunk partitions uniqueness'

            # Check chunk partitions and permutation equality.
            perms = np.sort(permutations[0])
            assert np.array_equal(unique, perms), 'failed chunk partitions and permutation equality'
    # Check uniqueness of the sample buffer indexes.
    if is_shuffled:
        for index in range(0, len(sample_buffer_indexes_list)-1):
            assert not np.array_equal(sample_buffer_indexes_list[index],
                                      sample_buffer_indexes_list[index+1]), \
                    'failed sample buffer indexes uniqueness'


def test_single_process(capfd, samples, targets, max_epochs, batch_size) -> None:
    ds = ZarrIterableDataset(samples=samples,
                             targets=targets,
                             shuffle_chunks=True,
                             chunks_shuffle_seed=1,
                             shuffle_buffer=True,
                             buffer_shuffle_seed=None)
    da = ZarrDataLoader(dataset=ds, num_workers=0, batch_size=batch_size, drop_last=False)
    _core_test(da, max_epochs, samples, True, capfd)



def test_multi_processes(capfd, samples, targets, max_epochs, num_workers,
                         prefetch_factor, batch_size) -> None:
    ds = ZarrIterableDataset(samples=samples,
                             targets=targets,
                             shuffle_chunks=True,
                             chunks_shuffle_seed=1,
                             shuffle_buffer=True,
                             buffer_shuffle_seed=None)
    da = ZarrDataLoader(dataset=ds,
                        num_workers=num_workers,
                        batch_size=batch_size,
                        drop_last=False,
                        multiprocessing_context='fork',
                        pin_memory=True,
                        prefetch_factor=prefetch_factor)
    _core_test(da, max_epochs, samples, True, capfd)


def test_target_as_zarr(capfd) -> None:
    samples = create_zarr_array(13)
    ds = ZarrIterableDataset(samples=samples,
                             targets=samples,
                             shuffle_chunks=True,
                             chunks_shuffle_seed=1,
                             shuffle_buffer=True,
                             buffer_shuffle_seed=None)
    da = ZarrDataLoader(dataset=ds,
                        batch_size=7,
                        num_workers=0,
                        drop_last=False)
    _core_test(da, 1, samples, True, capfd)


def test_target_as_pandas_series(capfd) -> None:
    samples = create_zarr_array(13)
    targets = pd.Series(np.arange(samples.shape[0])).to_numpy()
    ds = ZarrIterableDataset(samples=samples,
                             targets=targets,
                             shuffle_chunks=True,
                             chunks_shuffle_seed=1,
                             shuffle_buffer=True,
                             buffer_shuffle_seed=None)
    da = ZarrDataLoader(dataset=ds,
                        num_workers=0,
                        batch_size=7,
                        drop_last=False)
    _core_test(da, 1, samples, True, capfd)


@pytest.fixture(params=[-3, [], (), {1}, (-999, 0, 1), -999, -1, np.array((1,)), np.arange(10), \
                       [1], 1, (1,), (0,), (7,), (-1,), (-2,), (0, 1), (-3, -2, -1), (999,)])
def chunk_indexes_params(request, samples) -> ChunkIndexParams:
    buffer = list()
    try:
        if isinstance(request.param, int):
            buffer.append(samples.blocks[request.param])
        else:
            for chunk_index in request.param:
                buffer.append(samples.blocks[chunk_index])
        expected_sequence = np.concatenate(buffer)
    except Exception:
        expected_sequence = np.empty(0)
    expected_chunk_indexes = list()
    if isinstance(request.param, int):
        expected_chunk_indexes.append(request.param)
    else:
        for chunk_index in request.param:
            expected_chunk_indexes.append(chunk_index)
    return ChunkIndexParams(samples=samples, selected_chunk_indexes=request.param,
                            expected_sequence=expected_sequence,  # type: ignore
                            expected_chunk_indexes=expected_chunk_indexes)


def test_chunk_indexes(capfd, chunk_indexes_params, num_workers):
    exception = None
    try:
        ds = ZarrIterableDataset(samples=chunk_indexes_params.samples,
                                 targets=chunk_indexes_params.samples,
                                 selected_chunk_indexes=chunk_indexes_params.selected_chunk_indexes,
                                 shuffle_chunks=False,
                                 chunks_shuffle_seed=1,
                                 shuffle_buffer=False,
                                 buffer_shuffle_seed=None)
        assert np.array_equal(ds.selected_chunk_indexes, chunk_indexes_params.expected_chunk_indexes)
        da = ZarrDataLoader(dataset=ds,
                            num_workers=num_workers,
                            batch_size=17,
                            drop_last=False,
                            multiprocessing_context='fork')
        _core_test(da, 1, chunk_indexes_params.expected_sequence, False, capfd)
    except (ValueError, TypeError) as e:
        exception = e

    if exception is not None:
        str_exception = str(exception)
        assert 'unsupported chunk splitting' in str_exception  or \
               'one or several chunk indexes' in str_exception or \
               'empty list of chunk indexes' in str_exception  or \
               'unsupported type for selected chunk indexes' in str_exception, \
                   f'fail raising exception ({str_exception})'
