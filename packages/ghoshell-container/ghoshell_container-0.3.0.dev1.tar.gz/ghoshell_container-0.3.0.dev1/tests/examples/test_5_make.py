import pytest
from ghoshell_container import Container


class _Foo:
    pass


class _Bar(_Foo):
    pass


class _Baz:
    def __init__(self, foo: _Foo) -> None:
        self.foo = foo


class _Zoo:
    def __init__(self, foo: _Foo, a: int) -> None:
        self.foo = foo
        self.a = a


class _Cat:
    def __init__(self, foo: _Foo, zoo: _Zoo) -> None:
        self.foo = foo
        self.zoo = zoo


def test_make():
    c = Container()
    assert isinstance(c.make(_Foo), _Foo)


def test_make_with_kwargs():
    c = Container()
    zoo = c.make(_Zoo, a=2)
    assert isinstance(zoo, _Zoo)
    assert zoo.a == 2


def test_make_exception_without_kwargs():
    c = Container()
    with pytest.raises(RuntimeError):
        zoo = c.make(_Zoo)


def test_make_with_bind():
    c = Container()
    c.bind(_Foo, _Bar)
    assert isinstance(c.make(_Foo), _Bar)


def test_make_with_di():
    c = Container()
    c.bind(_Foo, _Bar)
    assert isinstance(c.make(_Baz), _Baz)
    assert isinstance(c.make(_Baz).foo, _Bar)


def test_recursive_make():
    import threading
    c = Container()
    c.bind(_Foo, _Bar)
    c.bind(_Zoo, kwargs=dict(a=1))

    def assert_zoo():
        zoo = c.make(_Zoo)
        assert isinstance(zoo, _Zoo)
        assert zoo.a == 1
        assert isinstance(zoo.foo, _Bar)

    # single time
    assert_zoo()

    ths = []
    # concurrent making
    for i in range(10):
        t = threading.Thread(target=assert_zoo)
        t.start()
        ths.append(t)
    for t in ths:
        t.join()
