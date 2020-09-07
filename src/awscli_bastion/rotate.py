"""Rotate IAM user AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY_ID utilities."""
import time
from typing import Any

import boto3
import botocore

from . import credentials

# from typing import TypedDictclass

# import datetime


SESSION: boto3.session.Session = boto3.Session()

# StsResponseCredentials(TypedDict):
#     AccessKeyId: str
#     SecretAccessKey: str
#     SessionToken: str
#     Expiration: datetime.datetime

# StsResponse(TypedDict):
#     Credentials: StsResponseCredentials


def _invalidate(
    client: botocore.client.IAM, username: str, should_delete: bool
) -> None:
    """Deactivate the IAM user's access key and secret access key.

    Args:
        client: boto3 IAM Client.
        username: The name of the IAM user associated with the access key.
        should_delete: Delete the IAM user's access key and secret access key.
    """
    pass


def _create(client: botocore.client.IAM, username: str) -> Any:
    """Create aws access key for the bastion profile.

    Args:
        client: boto3 IAM Client.
        username: The name of the IAM user associated with the access key.

    Returns:
        Contains the response to a successful CreateAccessKey request.
    """
    return client.create_access_key(UserName=username)


def _wait_until_key_is_active(
    client: botocore.client.IAM, aws_access_key_id: str
) -> None:
    """Wait until the AWS_ACCESS_KEY_ID is active.

    Args:
        client: boto3 IAM Client.
        aws_access_key_id: The AWS_ACCESS_KEY_ID to wait for an active status.
    """
    iam = boto3.client("iam")
    access_keys = iam.list_access_keys()["AccessKeyMetadata"]
    access_key_id_to_status = {
        access_key["AccessKeyId"]: access_key["Status"] for access_key in access_keys
    }

    while True:
        if access_key_id_to_status[aws_access_key_id] == "Active":
            break
        else:
            time.sleep(1)


def rotate(username: str = "", should_delete: bool = False) -> None:
    """Rotate AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY for IAM user.

    Args:
        username: The name of the IAM user associated with the access key.
        should_delete: Delete the IAM user's access key and secret access key.
    """
    client = SESSION.client("iam")

    username = username if username else client.get_user()["User"]["UserName"]

    _invalidate(client, username, should_delete)
    response = _create(client, username)
    _wait_until_key_is_active(client, response["AccessKey"]["AccessKeyId"])

    credentials
