import time

import tests.utils

####################################################################################################
# uv run scalene --no-browser --html --profile-all --memory-leak-detector tests/it_ds_mem_profiling.py > profile.html
# rm -f profile.html profile.json

# uv run mprof run --include-children --multiprocess tests/it_ds_mem_profiling.py
# uv run mprof plot
# uv run mprof clean
####################################################################################################


def test() -> None:
    num_workers = 4
    prefetch_factor = 2
    batch_size = 64
    max_epochs = 3
    print('> open dataset')
    samples, targets = tests.utils.open_dataset()
    print(f'> {samples.shape=}')

    print('> create dataset and dataloader')
    overall_start = time.perf_counter_ns()
    da = tests.utils.create_dataloader(samples=samples, targets=targets, num_workers=num_workers,
                                       batch_size=batch_size, prefetch_factor=prefetch_factor,
                                       drop_last=False)
    for epoch in range(max_epochs):
        print(f'> epoch #{epoch}')
        print('   > begin to iterate')
        epoch_start = time.perf_counter_ns()
        batch_count = 1
        batch_start = epoch_start
        for _ in da:
            intermediate_stop = time.perf_counter_ns()
            elapsed_time = tests.utils.display_duration((intermediate_stop-batch_start)/1e9)
            print(f'      > batch #{batch_count}: {elapsed_time}')
            batch_count += 1
            batch_start = intermediate_stop
        epoch_stop = time.perf_counter_ns()
        print(f'> epoch elapsed time: {tests.utils.display_duration((epoch_stop-epoch_start)/1e9)}')
    print(f'> overall elapsed time: {tests.utils.display_duration((time.perf_counter_ns()-overall_start)/1e9)}')

if __name__ == '__main__':
    tests.utils.set_logging_config()
    if tests.utils.DATASET_PATH.exists():
        test()
        print('> done')
        exit(0)
    else:
        print('> create dataset')
        tests.utils.create_dataset()
        print('> done')
        exit(-1)
