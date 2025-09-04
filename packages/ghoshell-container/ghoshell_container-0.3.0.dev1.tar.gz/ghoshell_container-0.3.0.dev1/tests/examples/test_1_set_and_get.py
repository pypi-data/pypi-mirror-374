from ghoshell_container import Container, IoCContainer


def test_set_and_get():
    container = Container()
    container.set('foo', 'bar')
    assert container.get('foo') == 'bar'
    assert container.bound('foo')


def test_get_none():
    container = Container()
    container.set('foo', 'bar')
    # if not set, get none
    assert container.get('zoo') is None
    assert container['foo'] is 'bar'
    del container['foo']
    assert container.get('foo') is None


def test_get_recursively():
    parent = Container()
    parent.set('foo', 'bar')

    child = Container(parent, name="self")
    assert child.name == 'self'
    assert child.parent is parent

    # child get contract from parent
    assert child.get('foo') == 'bar'
    # child get contract from self only
    assert child.get('foo', recursively=False) is None


def test_get_self():
    parent = Container()
    child = Container(parent, name="child")
    assert child.get(Container) is child
    assert parent.get(Container) is parent
    assert child is not parent
    assert child.get(IoCContainer) is child
    assert parent.get(IoCContainer) is parent
