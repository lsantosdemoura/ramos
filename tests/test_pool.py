# -*- coding: utf-8 -*-
try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator

import pytest

from ramos import configure
from ramos.compat import ImproperlyConfigured
from ramos.exceptions import InvalidBackendError
from ramos.mixins import ThreadSafeCreateMixin
from ramos.pool import BackendPool


class FakeABCBackend(ThreadSafeCreateMixin):
    id = 'fake_abc'


class FakeXYZBackend(ThreadSafeCreateMixin):
    id = 'fake_xyz'


class FakeBackendWithConstructor(ThreadSafeCreateMixin):
    id = 'fake_with_args'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class TestBackendPool(object):

    def test_get_backends_should_return_all_backends_classes(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backends = BackendPool.all_classes()

        assert issubclass(backends[0], FakeXYZBackend)
        assert issubclass(backends[1], FakeABCBackend)

    def test_get_backend_should_return_a_backend_class(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backend = BackendPool.get_class('fake_abc')
        assert issubclass(backend, FakeABCBackend)

    def test_iterator_should_return_an_interator_with_all_backends_instances(
        self
    ):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backends = BackendPool.iterator()
        assert isinstance(backends, Iterator)

        backend_0 = next(backends)
        backend_1 = next(backends)

        assert isinstance(backend_0, FakeXYZBackend)
        assert isinstance(backend_1, FakeABCBackend)

    def test_classes_iterator_should_return_an_interator_with_all_backends_classes(  # noqa
        self
    ):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backends = BackendPool.classes_iterator()
        assert isinstance(backends, Iterator)

        backend_0 = next(backends)
        backend_1 = next(backends)

        assert issubclass(backend_0, FakeXYZBackend)
        assert issubclass(backend_1, FakeABCBackend)

    def test_get_backends_should_return_all_backends_instances(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backends = BackendPool.all()

        assert isinstance(backends[0], FakeXYZBackend)
        assert isinstance(backends[1], FakeABCBackend)

    def test_get_backends_without_config_should_raise(self):
        configure(pools={})

        with pytest.raises(ImproperlyConfigured):
            BackendPool.all()

    def test_get_backends_with_zero_backends_should_return_empty_list(self):
        configure(pools={
            BackendPool.backend_type: {}
        })

        assert BackendPool.all() == []

    def test_get_should_return_the_backend_instance(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        backend = BackendPool.get('fake_abc')

        assert isinstance(backend, FakeABCBackend)

    def test_get_with_nonexistent_backend_should_raise(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeXYZBackend.__name__
                ),
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeABCBackend.__name__
                ),
            )
        })

        with pytest.raises(InvalidBackendError):
            BackendPool.get('fake_fake')

    def test_get_should_pass_args_to_the_backend_constructor(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeBackendWithConstructor.__name__
                ),
            )
        })

        backend = BackendPool.get(
            'fake_with_args',
            'arg1',
            'arg2',
            arg3=3,
            arg4=4
        )

        assert backend.args == ('arg1', 'arg2')
        assert backend.kwargs == {'arg3': 3, 'arg4': 4}

    def test_all_should_pass_args_to_the_backend_constructor(self):
        configure(pools={
            BackendPool.backend_type: (
                u'{module}.{cls}'.format(
                    module=__name__,
                    cls=FakeBackendWithConstructor.__name__
                ),
            )
        })

        backends = BackendPool.all('arg1', 'arg2', arg3=3, arg4=4)
        backend = backends[0]

        assert backend.args == ('arg1', 'arg2')
        assert backend.kwargs == {'arg3': 3, 'arg4': 4}
