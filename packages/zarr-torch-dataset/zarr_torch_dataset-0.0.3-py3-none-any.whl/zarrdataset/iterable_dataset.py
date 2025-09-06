import logging
import math
import typing

import numpy as np
import numpy.typing
import torch
import zarr

from zarrdataset.virtual_map import VirtualMap

_LOGGER = logging.getLogger(__name__)


def _get_gpu_info() -> tuple[int, int]:
    if torch.distributed.is_initialized():
        rank: int = torch.distributed.get_rank()  # Means the id of a GPU.
        world_size: int = torch.distributed.get_world_size()  # Means the number of GPUs.
    else:
        rank = 0
        world_size = 1
    return rank, world_size


def _get_worker_info() -> tuple[int, int]:
    if worker_info := torch.utils.data.get_worker_info():
        worker_id = worker_info.id
        num_workers = worker_info.num_workers
    else:
        worker_id = 0
        num_workers = 0
    return worker_id, num_workers


def _format_worker_log(msg: str) -> str:
    worker_id, _ = _get_worker_info()
    rank, _ = _get_gpu_info()
    result = f'[R{rank}][W{worker_id}]{msg}'
    return result


def _format_ndarray(array: numpy.typing.NDArray) -> str:
    result = np.array2string(array, max_line_width=500, separator=", ", threshold=500)
    result = result.replace('\n', ' ')
    result = result.strip()
    return result


class _ZarrIterator(typing.Iterator):
    def __init__(self,
                 *,
                 sample_buffer: VirtualMap | numpy.typing.NDArray,
                 target_buffer: VirtualMap | numpy.typing.NDArray | None,
                 shuffle_buffer: bool = True,
                 buffer_shuffle_seed: int | None) -> None:
        self.sample_buffer: VirtualMap | numpy.typing.NDArray = sample_buffer
        self.target_buffer: VirtualMap | numpy.typing.NDArray | None = target_buffer
        self.index_cursor: int = 0
        self.buffer_indexes: numpy.typing.NDArray[np.integer] = np.arange(self.sample_buffer.shape[0])

        if shuffle_buffer:
            if _LOGGER.isEnabledFor(logging.DEBUG):
                formatted_msg = _format_worker_log('[IT][STATUS] = "shuffling"')
                _LOGGER.debug(formatted_msg)
            rng = np.random.default_rng(buffer_shuffle_seed)
            rng.shuffle(self.buffer_indexes)

        if _LOGGER.isEnabledFor(logging.DEBUG) and len(self.sample_buffer.shape) <= 2:
            formatted_msg = _format_worker_log('[IT][BUFFER][SAMPLE_INDEXES] = ') + \
                            _format_ndarray(self.buffer_indexes)
            _LOGGER.debug(formatted_msg)

        # DataLoader of Pytorch doesn't known how to stack scalars.
        if len(self.sample_buffer.shape) == 1:
            self.return_sample_next_item_fn: typing.Callable = \
                _ZarrIterator._return_next_item_as_scalar
        else:
            self.return_sample_next_item_fn = _ZarrIterator._return_next_item_as_tensor

        if self.target_buffer is not None:
            if len(self.target_buffer.shape) == 1:
                self.return_target_next_item_fn: typing.Callable = \
                    _ZarrIterator._return_next_item_as_scalar
            else:
                self.return_target_next_item_fn = _ZarrIterator._return_next_item_as_tensor

    def __iter__(self) -> typing.Iterator:
        return self

    def __next__(self) -> torch.Tensor | typing.Any | \
            tuple[torch.Tensor | typing.Any, torch.Tensor | typing.Any]:
        if self.index_cursor < self.buffer_indexes.shape[0]:
            current_index = self.buffer_indexes[self.index_cursor]
            self.index_cursor += 1
            sample = self.return_sample_next_item_fn(self.sample_buffer, current_index)
            if self.target_buffer is not None:
                target = self.return_target_next_item_fn(self.target_buffer, current_index)
                return sample, target
            else:
                return sample
        else:
            raise StopIteration()

    @staticmethod
    def _return_next_item_as_scalar(buffer: numpy.typing.NDArray, buffer_index: int) -> typing.Any:
        return buffer[buffer_index]

    @staticmethod
    def _return_next_item_as_tensor(buffer: numpy.typing.NDArray, buffer_index: int) -> torch.Tensor:
        return torch.from_numpy(buffer[buffer_index])


# TODO: optimize loading when num_workers == 0  and world_size == 1:
#         - load all the chunks not shuffled as self.samples[:]).
#         - targets as ndarray not extracted.
# May be sub classes.
class ZarrIterableDataset(torch.utils.data.IterableDataset):
    def __init__(self,
                 *,
                 samples: zarr.Array,
                 targets: zarr.Array | numpy.typing.NDArray | None,
                 selected_chunk_indexes: int | typing.Sequence[int] |
                                         numpy.typing.NDArray[np.integer] | None = None,  # noqa
                 shuffle_chunks: bool = True,
                 chunks_shuffle_seed: int | None = None,
                 shuffle_buffer: bool = True,
                 buffer_shuffle_seed: int | None = None):
        self.samples: zarr.Array = samples
        self.targets: zarr.Array | numpy.typing.NDArray | None = targets
        self.sample_buffer: VirtualMap | numpy.typing.NDArray | None = None
        self.target_buffer: VirtualMap | numpy.typing.NDArray | None = None
        self.shuffle_chunks: bool = shuffle_chunks
        self.shuffle_buffer: bool = shuffle_buffer
        self.chunks_shuffle_seed: int | None = chunks_shuffle_seed
        self.buffer_shuffle_seed: int | None = buffer_shuffle_seed

        if selected_chunk_indexes is None:
            self.selected_chunk_indexes: numpy.typing.NDArray = np.arange(samples.nchunks)
        elif isinstance(selected_chunk_indexes, int):
            self.selected_chunk_indexes = np.array((selected_chunk_indexes,))
        elif len(selected_chunk_indexes) > 0:
            if isinstance(selected_chunk_indexes, typing.Sequence):
                self.selected_chunk_indexes = np.array(selected_chunk_indexes)
            elif isinstance(selected_chunk_indexes, np.ndarray):
                self.selected_chunk_indexes = selected_chunk_indexes
            else:
                raise TypeError('unsupported type for selected chunk indexes. ' +
                                f'Got {type(selected_chunk_indexes)}')
        else:
            raise ValueError('empty list of chunk indexes')

        self._check()

    def _check(self) -> None:
        if self.shuffle_chunks and self.chunks_shuffle_seed is None:
            raise ValueError('shuffle chunks is asked but chunks_shuffle_seed is missing')

        if self.targets is not None:
            len_targets = self.targets.shape[0] if isinstance(self.targets, zarr.Array) else \
                          len(self.targets)
            if self.samples.shape[0] != len_targets:
                raise ValueError('samples and targets must share the same first dimension value.' +
                                 f' Got {self.samples.shape[0]} for samples and {len_targets} ' +
                                 'for targets')

        sorted_chunk_indexes = np.sort(self.selected_chunk_indexes)
        if sorted_chunk_indexes[-1] >= self.samples.nchunks:
            raise ValueError('one or several chunk indexes are greater than the number of chunks.' +
                             f' Got {sorted_chunk_indexes[-1]} for {self.samples.nchunks} ' +
                             'number of chunks')
        if sorted_chunk_indexes[0] < 0 and abs(sorted_chunk_indexes[0]) > self.samples.nchunks:
            raise ValueError('one or several chunk indexes are greater than the number of chunks.' +
                             f' Got {sorted_chunk_indexes[0]} for {self.samples.nchunks} ' +
                             'number of chunks')

    def __iter__(self) -> typing.Iterator:
        # Can't get rank, world_size and worker_info until distributed is ready so these instructions
        # must be not be in __init__.
        rank, world_size = _get_gpu_info()
        worker_id, num_workers = _get_worker_info()

        # We don't want to split chunks.
        worker_factor = num_workers if num_workers > 0 else 1
        if self.selected_chunk_indexes.shape[0] < world_size * worker_factor:
            raise ValueError('unsupported chunk splitting: the number of chunk indexes must be ' +
                             'greater or equal to the number of devices multiplied by number' +
                             f'of workers. Got {self.selected_chunk_indexes.shape[0]} chunk index(es), ' +
                             f'{world_size} device(s) and {num_workers} worker(s)')
        # Don't refill buffers for the next epoch.
        if self.sample_buffer is None:
            self._fill_buffers(rank=rank, world_size=world_size, worker_id=worker_id,
                               num_workers=num_workers)
        return _ZarrIterator(sample_buffer=self.sample_buffer,  # type: ignore
                             target_buffer=self.target_buffer,  # type: ignore
                             shuffle_buffer=self.shuffle_buffer,
                             buffer_shuffle_seed=self.buffer_shuffle_seed)

    def _fill_buffers(self, rank: int, world_size: int, worker_id: int, num_workers: int):
        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log('[DS][STATUS] = "init"')
            _LOGGER.debug(formatted_msg)

        # TODO: warning when len(chunk_indexes) == 1: shuffle entropy is null.
        if self.shuffle_chunks:
            rng = np.random.Generator(np.random.PCG64(self.chunks_shuffle_seed))
            # Reproducible permutation across all workers as seed value and rng generator type
            # are the same.
            chunk_indexes_to_be_extracted = rng.permutation(self.selected_chunk_indexes)
        else:
            chunk_indexes_to_be_extracted = self.selected_chunk_indexes
        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log('[DS][PERMUTATION] = ' +
                                               _format_ndarray(chunk_indexes_to_be_extracted))
            _LOGGER.debug(formatted_msg)
        if world_size > 1:
            # Select subset of indexes for each GPU.
            chunk_indexes_to_be_extracted = ZarrIterableDataset._select_subset_indexes(
                chunk_indexes_to_be_extracted, rank, world_size)
            if _LOGGER.isEnabledFor(logging.DEBUG):
                formatted_msg = _format_worker_log('[DS][CHUNKS_PARTITION][GPUS] = ' +
                                                   _format_ndarray(chunk_indexes_to_be_extracted))
                _LOGGER.debug(formatted_msg)
        if num_workers > 1:
            # Select a subset of indexes for each dataload workers.
            chunk_indexes_to_be_extracted = ZarrIterableDataset._select_subset_indexes(
                chunk_indexes_to_be_extracted, worker_id, num_workers)
        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log('[DS][CHUNKS_PARTITION][FINAL] = ' +
                                               _format_ndarray(chunk_indexes_to_be_extracted))
            _LOGGER.debug(formatted_msg)

        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log('[DS][STATUS] = "loading samples"')
            _LOGGER.debug(formatted_msg)

        self.sample_buffer = ZarrIterableDataset._extract_zarr_chunks(self.samples,
                                                                      chunk_indexes_to_be_extracted)

        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log('[DS][STATUS] = "loading targets"')
            _LOGGER.debug(formatted_msg)

        if self.targets is not None:
            if isinstance(self.targets, zarr.Array):
                self.target_buffer = ZarrIterableDataset._extract_zarr_chunks(self.targets,
                                                                              chunk_indexes_to_be_extracted)
            elif isinstance(self.targets, np.ndarray):
                self.target_buffer = ZarrIterableDataset._extract_ndarray_chunks(self.targets,
                                                                                 chunk_indexes_to_be_extracted,
                                                                                 self.samples.chunks[0])
            else:
                raise ValueError(f'unsupported targets {type(self.targets)} type. Support only zarr array' +
                                 ' and numpy ndarray')
        del self.samples
        del self.targets

        if _LOGGER.isEnabledFor(logging.DEBUG):
            formatted_msg = _format_worker_log(f'[DS][BUFFER][SAMPLE_SHAPE] = {self.sample_buffer.shape}')
            _LOGGER.debug(formatted_msg)
            if self.target_buffer is not None:
                formatted_msg = _format_worker_log(f'[DS][BUFFER][TARGET_SHAPE] = {self.target_buffer.shape}')
                _LOGGER.debug(formatted_msg)
            formatted_msg = _format_worker_log('[DS][STATUS] = "ready"')
            _LOGGER.debug(formatted_msg)

    @staticmethod
    def _core_extract_ndarray_chunk(array: numpy.typing.NDArray,
                                    chunk_size: int,
                                    chunk_index: int) -> numpy.typing.NDArray:
        start_index = chunk_index * chunk_size
        stop_index = min(start_index + chunk_size, array.shape[0])
        return array[start_index: stop_index]

    @staticmethod
    def _extract_ndarray_chunks(array: numpy.typing.NDArray,
                                chunk_indexes_to_be_extracted: numpy.typing.NDArray[np.integer],
                                chunk_size: int) -> numpy.typing.NDArray | VirtualMap:
        if len(chunk_indexes_to_be_extracted) == 1:
            return ZarrIterableDataset._core_extract_ndarray_chunk(
                array=array,
                chunk_index=typing.cast(int, chunk_indexes_to_be_extracted[0]),
                chunk_size=chunk_size)
        else:
            buffer: list = list()
            for chunk_index in chunk_indexes_to_be_extracted:
                chunk = ZarrIterableDataset._core_extract_ndarray_chunk(
                    array=array,
                    chunk_index=typing.cast(int, chunk_index),
                    chunk_size=chunk_size)
                buffer.append(chunk)
            return VirtualMap(buffer)

    @staticmethod
    def _extract_zarr_chunks(array: zarr.Array,
                             chunk_indexes_to_be_extracted: numpy.typing.NDArray[np.integer]) \
            -> numpy.typing.NDArray | VirtualMap:
        if len(chunk_indexes_to_be_extracted) == 1:
            chunk = array.blocks[chunk_indexes_to_be_extracted[0]]
            result: numpy.typing.NDArray | VirtualMap = typing.cast(numpy.typing.NDArray, chunk)
        else:
            chunks = [array.blocks[chunk_index] for chunk_index in chunk_indexes_to_be_extracted]
            result = VirtualMap(typing.cast(typing.Sequence[numpy.typing.NDArray], chunks))
        return result

    @staticmethod
    def _select_subset_indexes(indexes: numpy.typing.NDArray[np.integer], id: int, size: int) \
            -> numpy.typing.NDArray[np.integer]:
        len_indexes = indexes.shape[0]
        nb_chunks_per_unit = int(math.ceil(len_indexes / size))
        start = nb_chunks_per_unit * id
        stop = min(start+nb_chunks_per_unit, len_indexes)
        return indexes[start:stop]


class ZarrDataLoader(torch.utils.data.DataLoader):
    def __init__(self,
                 *,
                 dataset: ZarrIterableDataset,
                 num_workers: int = 0,
                 batch_size: int = 1,
                 drop_last: bool = False,
                 pin_memory: bool = False,
                 multiprocessing_context: str | None = None,
                 prefetch_factor: int | None = None):
        # We don't want to split chunks.
        if dataset.selected_chunk_indexes.shape[0] < num_workers:
            raise ValueError('unsupported chunk splitting: the number of chunk indexes must be ' +
                             'greater or equal to the number of devices multiplied by number' +
                             f'of workers. Got {dataset.selected_chunk_indexes.shape[0]} chunk index(es), ' +
                             f'and {num_workers} worker(s)')
        super().__init__(dataset=dataset,
                         num_workers=num_workers,
                         batch_size=batch_size,
                         drop_last=drop_last,
                         pin_memory=pin_memory,
                         multiprocessing_context=multiprocessing_context,
                         persistent_workers=num_workers > 0,
                         prefetch_factor=prefetch_factor)
