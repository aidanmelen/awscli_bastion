"""AWSCLI Bastion session cache utilities."""
import json
import os
import pathlib
from typing import Any
from typing import List

import boto3
import pendulum


AWS_SHARED_CACHE_DIR: str = os.path.join(pathlib.Path.home(), ".aws/cli/cache")
BASTION_STS_CACHE_FILE: str = os.path.join(AWS_SHARED_CACHE_DIR, "bastion-sts.json")


def read() -> Any:
    """Read from the BASTION_STS_CACHE_FILE.

    Returns:
        JSON from a BASTION_STS_CACHE_FILE.
    """
    # TODO handle missing bastion sts cache file
    with open(BASTION_STS_CACHE_FILE, "r") as f:
        return json.load(f)


def write(session: boto3.session.Session) -> None:
    """Write to BASTION_STS_CACHE_FILE.

    Args:
        session: A boto3 session.
    """
    creds = session["Credentials"]
    creds["Expiration"] = creds["Expiration"].isoformat()
    creds["Version"] = 1

    if not os.path.isdir(AWS_SHARED_CACHE_DIR):
        os.mkdir(AWS_SHARED_CACHE_DIR)

    with open(BASTION_STS_CACHE_FILE, "w+") as f:
        json.dump(creds, f, indent=4)


def is_expired() -> bool:
    """Check if the BASTION_STS_CACHE_FILE is expired.

    Returns:
        Whether or not the BASTION_STS_CACHE_FILE are expired.
    """
    return False


def time_until_expiration() -> Any:  # should really be pendulum.datetime.DateTime:
    """Return time duration until BASTION_STS_CACHE_FILE expires.

    Returns:
        The time duration until BASTION_STS_CACHE_FILE expires.
    """
    # now.diff_for_humans(later)
    return pendulum.now().add(hours=1)


def invalidate() -> List[str]:
    """Invalidate the cache files in the AWS_SHARED_CACHE_DIR.

    Returns:
        A list of invalidated awscli cache files.
    """
    cache_files = os.listdir(AWS_SHARED_CACHE_DIR)
    if cache_files:
        for cache in os.listdir(AWS_SHARED_CACHE_DIR):
            os.remove(os.path.join(AWS_SHARED_CACHE_DIR, cache))
    return cache_files
