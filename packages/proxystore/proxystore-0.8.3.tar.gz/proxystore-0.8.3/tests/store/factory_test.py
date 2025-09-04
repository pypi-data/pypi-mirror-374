from __future__ import annotations

import time

import pytest

from proxystore.connectors.local import LocalConnector
from proxystore.serialize import deserialize
from proxystore.serialize import serialize
from proxystore.store import Store
from proxystore.store import store_registration
from proxystore.store.exceptions import ProxyResolveMissingKeyError
from proxystore.store.factory import PollingStoreFactory

FactoryT = PollingStoreFactory[LocalConnector, str]


def test_polling_store_factory_resolve() -> None:
    with Store('polling-store-factory-resolve', LocalConnector()) as store:
        with store_registration(store):
            value = 'test-value'
            key = store.put(value)
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
            )
            assert factory.resolve() == value
            assert factory() == value


def test_polling_store_factory_evict() -> None:
    with Store('polling-store-factory-evict', LocalConnector()) as store:
        with store_registration(store):
            value = 'test-value'
            key = store.put(value)
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
                evict=True,
            )
            assert factory.resolve() == value
            assert not store.exists(key)


def test_polling_store_factory_metrics() -> None:
    with Store(
        'polling-store-factory-metrics',
        LocalConnector(),
        metrics=True,
    ) as store:
        with store_registration(store):
            value = 'test-value'
            key = store.put(value)
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
            )
            assert factory.resolve() == value

            assert store.metrics is not None
            metrics = store.metrics.get_metrics(key)
            assert metrics is not None
            assert 'factory.polling_resolve' in metrics.times


def test_polling_store_factory_timeout() -> None:
    with Store('polling-store-factory-timeout', LocalConnector()) as store:
        with store_registration(store):
            key = store.connector.new_key()
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
                evict=True,
                polling_interval=0.001,
                polling_timeout=0.002,
            )
            with pytest.raises(ProxyResolveMissingKeyError):
                factory.resolve()


def test_polling_store_factory_backoff() -> None:
    with Store('polling-store-factory-backoff', LocalConnector()) as store:
        with store_registration(store):
            key = store.connector.new_key()
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
                evict=True,
                polling_interval=0.001,
                polling_backoff_factor=2,
                polling_interval_limit=0.004,
                polling_timeout=0.011,
            )
            start = time.perf_counter()
            with pytest.raises(ProxyResolveMissingKeyError):
                factory.resolve()
            end = time.perf_counter()

            # polling_timeout is 0.011 so we should sleep for 0.001, 0.002,
            # 0.004, and 0.004 seconds then timeout
            min_sleep = 0.011
            assert (end - start) > min_sleep


def test_polling_store_factory_serialize() -> None:
    with Store('polling-store-factory-serialize', LocalConnector()) as store:
        with store_registration(store):
            value = 'test-value'
            key = store.put(value)
            factory: FactoryT = PollingStoreFactory(
                key=key,
                store_config=store.config(),
            )
            factory = deserialize(serialize(factory))
            assert factory.resolve() == value
            assert factory() == value
