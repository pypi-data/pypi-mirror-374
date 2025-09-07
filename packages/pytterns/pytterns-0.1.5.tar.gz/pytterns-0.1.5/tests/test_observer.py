import pytest
from pytterns import observer, load
from pytterns.core.decorators import OBSERVERS


@pytest.fixture(autouse=True)
def reset_observers():
    orig = OBSERVERS.copy()
    OBSERVERS.clear()
    try:
        yield
    finally:
        OBSERVERS.clear()
        OBSERVERS.update(orig)


def test_register_function_listener_and_notify():
    called = {}

    @observer('evt')
    def listener(x):
        called['v'] = x
        return 'ok'

    res = load.observer('evt').notify(5)
    assert any(success and result == 'ok' for success, result in res)
    assert called['v'] == 5


def test_register_class_listener_and_notify():
    @observer('evt2')
    class L:
        def __init__(self):
            self.last = None

        def update(self, x, y=0):
            self.last = (x, y)
            return 'class'

    out = load.observer('evt2').notify(1, y=2)
    assert any(success and result == 'class' for success, result in out)


def test_listener_exception_is_captured():
    @observer('evt3')
    def bad(x):
        raise RuntimeError('fail')

    @observer('evt3')
    def good(x):
        return 'ok'

    results = load.observer('evt3').notify('p')
    # Expect one failure and one success
    assert sum(1 for s, _ in results if not s) == 1
    assert sum(1 for s, _ in results if s) == 1


def test_notify_nonexistent_event_raises():
    with pytest.raises(ValueError):
        load.observer('nope')


def test_observer_unsubscribe():
    @observer('tmp')
    def f(x):
        return x

    loader = load.observer('tmp')
    # unsubscribe by function reference
    loader.unsubscribe(f)
    # now there should be no listeners
    with pytest.raises(ValueError):
        load.observer('tmp')
