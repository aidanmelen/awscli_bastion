"""AWSCLI Bastion AWS_SHARED_CREDENTIALS_FILE utilities."""
import configparser
import os
import pathlib
from typing import Any
from typing import List


CONFIG: configparser.ConfigParser = configparser.ConfigParser()
AWS_SHARED_CREDENTIALS_FILE: str = os.environ.get(
    "AWS_SHARED_CREDENTIALS_FILE", f"{pathlib.Path.home()}/.aws/credentials"
)


def read() -> None:
    """Read from AWS_SHARED_CREDENTIALS_FILE."""
    CONFIG.read(AWS_SHARED_CREDENTIALS_FILE)


def write() -> None:
    """Write to AWS_SHARED_CREDENTIALS_FILE."""
    with open(AWS_SHARED_CREDENTIALS_FILE, "w") as f:
        CONFIG.write(f)


def set_profile(profile_name: str, sts_response: Any) -> None:
    """Write to STS session credentials into profile section of configparser.

    Args:
        profile_name: The AWS_SHARED_CREDENTIALS_FILE profile name.
        sts_response: sts.get_session_token() or sts.assume_role() response.
    """
    CONFIG[profile_name]["aws_access_key_id"] = sts_response["Credentials"][
        "AccessKeyId"
    ]
    CONFIG[profile_name]["aws_secret_access_key"] = sts_response["Credentials"][
        "SecretAccessKey"
    ]
    CONFIG[profile_name]["aws_session_token"] = sts_response["Credentials"][
        "SessionToken"
    ]
    CONFIG[profile_name]["aws_session_expiration"] = sts_response["Credentials"][
        "Expiration"
    ]


def invalidate() -> List[str]:
    """Invalidate aws profiles credentials that use bastion-sts profile.

    Returns:
        A list of invalidated profile names from the AWS_SHARED_CREDENTIALS_FILE.
    """
    # TODO
    return ["bastion-sts"]
