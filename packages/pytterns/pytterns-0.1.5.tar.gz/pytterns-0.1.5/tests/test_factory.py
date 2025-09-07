import pytest
from pytterns import factory, load
from pytterns.core.decorators import FACTORIES


@pytest.fixture(autouse=True)
def reset_factories():
    orig = FACTORIES.copy()
    FACTORIES.clear()
    try:
        yield
    finally:
        FACTORIES.clear()
        FACTORIES.update(orig)


def test_factory_creates_instance():
    @factory('svc')
    class Service:
        def __init__(self, name):
            self.name = name

    inst = load.factory('svc').create('x')
    assert inst.__class__.__name__ == 'Service'
    assert inst.name == 'x'


def test_factory_missing_raises():
    with pytest.raises(ValueError):
        load.factory('nope')


def test_factory_create_with_index():
    @factory('svc2')
    class A:
        def __init__(self):
            self.tag = 'A'

    @factory('svc2')
    class B:
        def __init__(self):
            self.tag = 'B'

    a = load.factory('svc2').create(index=0)
    b = load.factory('svc2').create(index=1)
    assert a.tag == 'A'
    assert b.tag == 'B'
    with pytest.raises(IndexError):
        load.factory('svc2').create(index=2)
