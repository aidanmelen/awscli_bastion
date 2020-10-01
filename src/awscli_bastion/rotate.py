"""Rotate IAM user AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY_ID module."""
import logging
import time
from typing import Any
from typing import Optional

import boto3
import click
from botocore.exceptions import ClientError

from .credentials import Credentials


logger = logging.getLogger(__name__)


class Rotate:
    """Rotate IAM user AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY_ID module."""

    def __init__(
        self,
        deactivate: bool = False,
        username: Optional[str] = None,
        bastion: str = "bastion",
        bastion_sts: str = "bastion-sts",
        region: str = "us-west-2",
        credentials: Optional[Credentials] = None,
    ) -> None:
        """Rotate Init."""
        self.deactivate = deactivate
        self.bastion = bastion
        self.region = region
        self.credentials = credentials

        try:
            self.bastion_session = boto3.Session(
                profile_name=bastion, region_name=self.region
            )
            self.bastion_sts_session = boto3.Session(
                profile_name=bastion_sts, region_name=self.region
            )

            iam = self.bastion_session.client("iam")
            self.username = username if username else iam.get_user()["User"]["UserName"]
        except ClientError as e:
            raise click.ClickException(str(e))

    def create_access_key(self) -> Any:
        """Create aws access key for the bastion profile."""
        try:
            iam_client = self.bastion_sts_session.client("iam")
            return iam_client.create_access_key(UserName=self.username)
        except ClientError as e:
            raise click.ClickExceptions(str(e))

    def _wait_until_key_is_active(self, client: Any, aws_access_key_id: str) -> None:
        """Wait until the AWS_ACCESS_KEY_ID is active.

        Args:
            client: boto3 IAM Client.
            aws_access_key_id: The AWS_ACCESS_KEY_ID to wait for an active status.
        """
        iam = self.bastion_session.client("iam")
        access_keys = iam.list_access_keys()["AccessKeyMetadata"]
        access_key_id_to_status = {
            access_key["AccessKeyId"]: access_key["Status"]
            for access_key in access_keys
        }

        while True:
            if access_key_id_to_status[aws_access_key_id] == "Active":
                break
            else:
                time.sleep(1)

    def retire_bastion_access_key(self) -> None:
        """Retire aws access key for the bastion profile.

        By default, this means deletion. Specify the 'deactivate' class
        variable to deactivate.
        """
        bastion_aws_access_key_id = self.credentials.config.get(
            self.bastion, "aws_access_key_id", fallback=None
        )

        iam = self.bastion_sts_session.resource("iam")
        access_key = iam.AccessKey(self.username, bastion_aws_access_key_id)
        if self.deactivate:
            access_key.deactivate()
        else:
            access_key.delete()

        self.credentials.config[self.bastion]["aws_access_key_id"] = ""
        self.credentials.config[self.bastion]["aws_secret_access_key"] = ""

    def write(self, access_key: str) -> None:
        """Write access key to the bastion profile in the aws share credentials file.

        Arguments:
            access_key: The aws access key access key to write.
        """
        self.credentials.config[self.bastion]["aws_access_key_id"] = access_key[
            "AccessKey"
        ]["AccessKeyId"]
        self.credentials.config[self.bastion]["aws_secret_access_key"] = access_key[
            "AccessKey"
        ]["SecretAccessKey"]
        self.credentials.write()

    def rotate(self) -> None:
        """Rotate aws access key credentials for the bastion profile."""
        access_key = self.create_access_key()
        self._wait_until_key_is_active(access_key)
        self.retire_bastion_access_key()
        self.write(access_key)
        click.echo(f"Rotated long-lived credentials for the {self.bastion} profile.")
