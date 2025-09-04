from __future__ import annotations

import os
import pathlib
import uuid
from collections.abc import Generator
from unittest import mock

import pytest
from globus_sdk.globus_app import ClientApp
from globus_sdk.globus_app import UserApp
from globus_sdk.tokenstorage import MemoryTokenStorage

from proxystore.globus.app import get_client_app
from proxystore.globus.app import get_client_credentials_from_env
from proxystore.globus.app import get_globus_app
from proxystore.globus.app import get_token_storage
from proxystore.globus.app import get_user_app
from proxystore.globus.app import is_client_login
from proxystore.globus.app import PROXYSTORE_GLOBUS_CLIENT_ID_ENV_NAME
from proxystore.globus.app import PROXYSTORE_GLOBUS_CLIENT_SECRET_ENV_NAME


@pytest.fixture
def mock_env_credentials() -> Generator[tuple[str, str], None, None]:
    client_uuid = str(uuid.uuid4())
    client_secret = 'secret'

    env = {
        PROXYSTORE_GLOBUS_CLIENT_ID_ENV_NAME: client_uuid,
        PROXYSTORE_GLOBUS_CLIENT_SECRET_ENV_NAME: client_secret,
    }
    with mock.patch.dict(os.environ, env):
        yield client_uuid, client_secret


def test_get_token_storage(tmp_path: pathlib.Path):
    filepath = tmp_path / 'tokens.db'
    storage = get_token_storage(filepath)
    assert filepath.is_file()
    storage.close()


def test_get_token_storage_adapter_proxystore_default(
    tmp_path: pathlib.Path,
) -> None:
    parent_dir = tmp_path / 'storage'
    with mock.patch(
        'proxystore.globus.app.home_dir',
        return_value=str(parent_dir),
    ):
        storage = get_token_storage()

    assert parent_dir.exists()
    assert len(list(parent_dir.glob('*.db'))) == 1
    storage.close()


def test_get_confidential_app_auth_client_from_env(
    mock_env_credentials,
) -> None:
    found_id, found_secret = get_client_credentials_from_env()
    assert found_id == mock_env_credentials[0]
    assert found_secret == mock_env_credentials[1]


@mock.patch('proxystore.globus.app.get_token_storage')
def test_get_globus_app_client_login(
    mock_storage,
    mock_env_credentials,
) -> None:
    mock_storage.return_value = MemoryTokenStorage()
    globus_app = get_globus_app()
    assert isinstance(globus_app, ClientApp)


@mock.patch('proxystore.globus.app.get_token_storage')
def test_get_globus_app_not_client_login(mock_storage) -> None:
    mock_storage.return_value = MemoryTokenStorage()
    globus_app = get_globus_app()
    assert isinstance(globus_app, UserApp)


@mock.patch('proxystore.globus.app.get_token_storage')
def test_get_client_app_from_env(mock_storage, mock_env_credentials) -> None:
    mock_storage.return_value = MemoryTokenStorage()
    globus_app = get_client_app()
    assert isinstance(globus_app, ClientApp)


@mock.patch('proxystore.globus.app.get_token_storage')
def test_get_client_app_custom(mock_storage) -> None:
    mock_storage.return_value = MemoryTokenStorage()
    globus_app = get_client_app(str(uuid.uuid4()), '<secret>')
    assert isinstance(globus_app, ClientApp)


@mock.patch('proxystore.globus.app.get_token_storage')
def test_get_user_app(mock_storage) -> None:
    mock_storage.return_value = MemoryTokenStorage()
    globus_app = get_user_app()
    assert isinstance(globus_app, UserApp)


def test_is_client_login() -> None:
    with mock.patch.dict(os.environ, {}):
        assert not is_client_login()

    env = {PROXYSTORE_GLOBUS_CLIENT_ID_ENV_NAME: str(uuid.uuid4())}
    with mock.patch.dict(os.environ, env):
        assert not is_client_login()

    env[PROXYSTORE_GLOBUS_CLIENT_SECRET_ENV_NAME] = 'secret'
    with mock.patch.dict(os.environ, env):
        assert is_client_login()
