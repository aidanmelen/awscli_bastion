"""AWSCLI Bastion AWS_SHARED_CREDENTIALS_FILE module."""
import configparser
import logging
import os
import pathlib
from typing import Any
from typing import Union

import boto3
import click
import pendulum
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class Credentials:
    """AWSCLI Bastion AWS_SHARED_CREDENTIALS_FILE module."""

    def __init__(self) -> None:
        """Credentials Init."""
        self.aws_shared_credentials_file = os.environ.get(
            "AWS_SHARED_CREDENTIALS_FILE",
            os.path.join(pathlib.Path.home(), ".aws/credentials"),
        )
        self.config = configparser.ConfigParser()
        self.config.read(self.aws_shared_credentials_file)

    def write(self) -> None:
        """Write credentials to the AWS_SHARED_CREDENTIALS_FILE."""
        with open(self.aws_shared_credentials_file, "w") as f:
            self.config.write(f)

    def get(self, profile: str, item: str) -> str:
        """Get profile item from AWS_SHARED_CREDENTIALS_FILE.

        Arguments:
            profile: The profile that contains the item.
            item: The item to get from the profile.

        Raises:
            ClickException: Failed to get the item from profile.

        Returns:
            The profile item.
        """
        try:
            return self.config[profile][item]
        except Exception:
            raise click.ClickException(
                f"Failed to get the `{item}` from `{profile}` profile."
            )

    def get_expiration(
        self, profile: str = "bastion-sts", in_words: bool = True
    ) -> Union[str, Any]:
        """Return how much time until the bastion-sts credentials expire.

        Arguments:
            profile: The profile to expire.
            in_words: To print out the expiration in words.

        Returns:
            How much time until the bastion-sts credentials expire.
        """
        now_dt = pendulum.now()  # type: ignore
        expiration_iso = self.get(profile, "aws_session_expiration")
        expiration_dt = pendulum.parse(expiration_iso)  # type: ignore
        period = now_dt - expiration_dt
        return period.in_words() if in_words else period

    def is_expired(self, profile: str = "bastion-sts") -> bool:
        """Return if the bastion-sts credentials are expired.

        Arguments:
            profile: The profile that assume role profile's source.

        Returns:
            If the bastion-sts credentials are expired.
        """
        # TODO return true if is less that zero
        return bool(self.get_expiration(profile, in_words=False))

    def get_mfa_serial(self, profile: str = "bastion-sts") -> str:
        """Get the mfa serial number for the bastion IAM user.

        Arguments:
            profile: The profile that assume role profile's source.

        Returns:
            The identification number of the MFA device that is
            associated with the IAM user.
        """
        return self.get(profile, "mfa_serial")

    def set_mfa_serial(
        self, mfa_serial: Any = None, bastion_sts: str = "bastion_sts"
    ) -> None:
        """Set the `mfa_serial` attribute for the given profile.

        Arguments:
            mfa_serial: The identification number of the MFA device that is
                        associated with the IAM user.
            bastion_sts: The profile that assume role profile's source.

        Raises:
            ClickException: Failed to get `mfa_serial` from the IAM user.
        """
        if not mfa_serial:
            try:
                iam = boto3.client("iam")
                username = iam.get_user()["User"]["UserName"]

                for iam_mfa_device in iam.list_mfa_devices(UserName=username)[
                    "MFADevices"
                ]:
                    mfa_serial = iam_mfa_device["SerialNumber"]
                    break  # no need to check another MFA device.
                # else:
                #     click.ClickException(f"The {username} IAM user does not exist.")

            except ClientError as e:
                if e.response["Error"]["Code"] == "ValidationError":
                    raise click.ClickException(
                        "Failed to get the mfa serial number."
                        "Your IAM user must have `iam:get_user` and "
                        "`iam:list_mfa_devices` privileges."
                    )
                # else:
                #     click.ClickException(f"Unexpected error: {e}")
        self.config[bastion_sts]["mfa_serial"] = mfa_serial  # type: ignore

    def set_profile(self, sts_response: Any, profile: str) -> None:
        """Write to STS session credentials into a profile.

        Arguments:
            sts_response: `sts.get_session_token()` or `sts.assume_role()` response.
            profile: The profile name.
        """
        self.config[profile]["aws_access_key_id"] = sts_response["Credentials"][
            "AccessKeyId"
        ]
        self.config[profile]["aws_secret_access_key"] = sts_response["Credentials"][
            "SecretAccessKey"
        ]
        self.config[profile]["aws_session_token"] = sts_response["Credentials"][
            "SessionToken"
        ]
        self.config[profile]["aws_session_expiration"] = sts_response["Credentials"][
            "Expiration"
        ]

    def set_default(self, profile: str) -> None:
        """Set the default profile with attributes from another profile.

        Arguments:
            profile: The profile with a `role_arn` attribute.

        Raises:
            ClickException: Failed to get profile.
        """
        try:
            self.config["default"] = dict(self.config[profile])
        except Exception:
            raise click.ClickException(
                f"Failed to set default profile with attributes from the"
                f"`{profile}` profile. The `{profile}' profile is not defined "
                f"in the AWS_SHARED_CREDENTIALS_FILE."
            )

    def clear(self, bastion: str = "bastion") -> None:
        """Clear sts credentials from the AWS_SHARED_CREDENTIALS_FILE.

        Arguments:
            bastion: The profile containing the long-lived IAM credentials.
        """
        profiles = self.config.sections()

        # We don't want to remove the long-lived credentials.
        # So we remove it from the list of removal candidates.
        profiles.remove(bastion)

        click.echo(
            f"- Skipping the '{bastion}' profile because it may contain "
            f"long-lived credentials."
        )

        for profile in profiles:
            if "source_profile" not in self.config[profile]:
                click.echo(
                    f"- Skipping the '{profile}' profile because it may contain "
                    f"long-lived credentials."
                )
                continue

            is_access_key = "aws_access_key_id" in self.config[profile]
            is_secret_key = "aws_secret_access_key" in self.config[profile]
            is_session_token = "aws_session_token" in self.config[profile]
            is_expiration = "aws_session_expiration" in self.config[profile]

            if is_access_key:
                del self.config[profile]["aws_access_key_id"]
            if is_secret_key:
                del self.config[profile]["aws_secret_access_key"]
            if is_session_token:
                del self.config[profile]["aws_session_token"]
            if is_expiration:
                del self.config[profile]["aws_session_expiration"]

            if any([is_access_key, is_secret_key, is_session_token, is_expiration]):
                click.echo(
                    f"- STS credentials were removed from the {profile} profile."
                )
        self.write()
