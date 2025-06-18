import os
from test.settings import (
    ValidAppSettings,
    get_invalid_app_settings,
    get_valid_app_settings,
)

import pytest
from loguru import logger
from pydantic_core._pydantic_core import ValidationError


@pytest.mark.asyncio
async def test_valid_get_secret(disable_logging_exception, vault_container):
    # Read the vault credentials from the file
    credentials = vault_container.execute(["cat", "/vault-credentials.env"])
    credentials_dict = dict(line.split("=") for line in credentials.splitlines())
    role_id = credentials_dict.get("ROLE_ID")
    secret_id = credentials_dict.get("SECRET_ID")

    os.environ["VAULT_ROLE_ID"] = role_id
    os.environ["VAULT_SECRET_ID"] = secret_id

    vault_container.execute(
        ["vault", "kv", "put", "-mount=secret", "test", "FOO=BAR"],
        envs={"VAULT_ADDR": "http://127.0.0.1:8200"},
    )

    settings: ValidAppSettings = get_valid_app_settings()
    assert settings.FOO.get_secret_value() == "BAR"
    logger.info("Secret Found")


@pytest.mark.asyncio
async def test_invalid_get_secret(disable_logging_exception, vault_container):
    # Read the vault credentials from the file
    credentials = vault_container.execute(["cat", "/vault-credentials.env"])
    credentials_dict = dict(line.split("=") for line in credentials.splitlines())
    role_id = credentials_dict.get("ROLE_ID")
    secret_id = credentials_dict.get("SECRET_ID")

    os.environ["VAULT_ROLE_ID"] = role_id
    os.environ["VAULT_SECRET_ID"] = secret_id

    vault_container.execute(
        ["vault", "kv", "put", "-mount=secret", "test", "FOO=BAR"],
        envs={"VAULT_ADDR": "http://127.0.0.1:8200"},
    )

    with pytest.raises(ValidationError):
        # the secret UNKNOWN is not found
        get_invalid_app_settings()
