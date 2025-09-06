import numpy as np

from zarrdataset.virtual_map import VirtualMap


def test_virtual_map() -> None:
    a = np.arange(10)
    b = np.arange(10, 25)
    c = np.arange(25, 30)
    test = np.arange(30)
    vm = VirtualMap((a, b, c))

    assert vm[0] == test[0]
    assert vm[10] == test[10]
    assert vm[29] == test[29]
    assert vm[-1] == test[-1]
    assert vm[-2] == test[-2]
    assert vm[-30] == test[-30]
    assert vm[-10] == test[-10]
    assert vm[-20] == test[-20]

    assert np.array_equal(vm[:8], test[:8])
    assert np.array_equal(vm[1:8], test[1:8])
    assert np.array_equal(vm[2:8], test[2:8])

    assert np.array_equal(vm[10:18], test[10:18])
    assert np.array_equal(vm[11:18], test[11:18])
    assert np.array_equal(vm[12:18], test[12:18])

    assert np.array_equal(vm[:20], test[:20])
    assert np.array_equal(vm[9:27], test[9:27])
    assert np.array_equal(vm[-2:18], test[-2:18])
    assert np.array_equal(vm[-2:-18], test[-2:-18])
    assert np.array_equal(vm[-15:-3], test[-15:-3])
    assert np.array_equal(vm[-1:-10], test[-1:-10])
    assert np.array_equal(vm[-10:-20], test[-10:-20])
    assert np.array_equal(vm[:], test[:])
