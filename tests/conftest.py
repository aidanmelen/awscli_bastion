"""Package-wide test fixtures."""
import logging
import os
from typing import Any

import pytest
from pytest_mock import MockFixture

from . import mock_return_values


logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="session")
def ensure_test_credentials_are_used() -> Any:
    """Set AWS_SHARED_CREDENTIALS_FILE to use test-credentials."""
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.path.join(
        os.path.dirname(__file__), "test-credentials"
    )
    yield
    del os.environ["AWS_SHARED_CREDENTIALS_FILE"]


@pytest.fixture(autouse=True, scope="session")
def ensure_test_cache_is_used() -> Any:
    """Set AWSCLI_BASTION_STS_CACHE_FILE to use test-cache."""
    os.environ["AWSCLI_BASTION_STS_CACHE_FILE"] = os.path.join(
        os.path.dirname(__file__), "test-cache"
    )
    yield
    del os.environ["AWSCLI_BASTION_STS_CACHE_FILE"]


@pytest.fixture
def boto3_api_call(mocker: MockFixture) -> Any:
    """Fixture for mocking boto3.Session.client."""

    def _boto3_api_call_side_effect(*args: Any, **kwargs: Any) -> Any:
        """Returns a side effect mocked boto3 api response for method calls."""
        method_name = args[0]
        if method_name == "GetSessionToken":
            return mock_return_values.sts_get_session_token
        elif method_name == "AssumeRole":
            return mock_return_values.sts_assume_role
        elif method_name == "GetUser":
            return mock_return_values.iam_get_user
        elif method_name == "ListMFADevices":
            return mock_return_values.iam_list_mfa_devices
        elif method_name == "ListAccessKeys":
            return mock_return_values.iam_list_access_keys
        elif method_name == "CreateAccessKeys":
            return mock_return_values.iam_create_access_keys
        else:
            logger.error(
                f"The side effect cannot return because {method_name} has not "
                "been mocked."
            )

    return mocker.patch(
        "botocore.client.BaseClient._make_api_call",
        side_effect=_boto3_api_call_side_effect,
    )
