"""AWSCLI Bastion auth module."""
import logging
from typing import Any
from typing import Optional

import boto3
import click
import pendulum

from . import cache
from . import credentials

# from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class STS:
    """AWSCLI Bastion auth module."""

    ONE_HOUR_IN_SECONDS: int = pendulum.duration(hours=1).in_seconds()
    TWELVE_HOURS_IN_SECONDS: int = pendulum.duration(hours=12).in_seconds()

    def __init__(
        self,
        bastion: str = "bastion",
        bastion_sts: str = "bastion-sts",
        region: str = "us-west-2",
        cache: Optional[cache.Cache] = None,
        credentials: Optional[credentials.Credentials] = None,
    ) -> None:
        """STS init.

        Arguments:
            bastion: The profile containing the long-lived IAM credentials.
            bastion_sts: The profile that assume role profiles source.
            region: The region used when creating new AWS connections.
            credentials: The Credentials object.
            cache: The Cache object.
        """
        self.bastion = bastion
        self.bastion_sts = bastion_sts
        self.region = region
        self.credentials = credentials
        self.cache = cache

    def is_mfa_code_invalid(self, mfa_code: str) -> bool:
        """Returns if MFA code is valid.

        Arguments:
            mfa_code: The 6 digit MFA code.

        Returns:
            If MFA code is valid.
        """
        return len(mfa_code) != 6 or not mfa_code.isdigit()

    def _prompt_for_mfa_code(self, mfa_serial: str) -> int:
        """Prompt the user for the mfa code and return it.

        Arguments:
            mfa_serial: The identification number of the MFA device that is
                associated with the IAM user.

        Returns:
            A 6 digit mfa code
        """
        is_mfa_code_invalid = True
        while is_mfa_code_invalid:
            mfa_code = click.prompt(f"Enter MFA code for {mfa_serial}", hide_input=True)
            if self.is_mfa_code_invalid(mfa_code):
                click.echo(
                    "Warning: The MFA code must be 6 digits. For example: 123456"
                )
        return mfa_code

    def get_session_token(
        self,
        mfa_code: Optional[int] = None,
        mfa_serial: Optional[str] = None,
        duration_seconds: int = TWELVE_HOURS_IN_SECONDS,
    ) -> Any:
        """Get the short-lived credentials from STS get session token.

        Get new credentials if the `mfa_code` is provided. Otherwise, try to
        look up sts credentials from the cache.

        Arguments:
            mfa_code: The value provided by the MFA device.
            mfa_serial: The identification number of the MFA device that is
                associated with the IAM user.
            duration_seconds: The duration, in seconds, that the credentials
                should remain valid.

        Raises:
            ClickException: Failed to call `sts.get_session_token()`

        Returns:
            Contains the response to a successful GetSessionToken request,
            including temporary AWS credentials that can be used to make
            AWS requests.
        """
        if not mfa_serial:
            mfa_serial = self.credentials.get_mfa_serial(profile=self.bastion_sts)

        cached_sts_creds = None
        if not mfa_code and not self.cache.is_expired():
            cached_sts_creds = self.cache.read()

        if cached_sts_creds:
            sts_creds = cached_sts_creds
        else:
            if not mfa_code or self.is_mfa_code_invalid(mfa_code):
                mfa_code = self._prompt_for_mfa_code(mfa_serial)

            session = boto3.Session(profile_name=self.bastion, region_name=self.region)
            sts = session.client("sts")
            try:
                sts_creds = sts.get_session_token(
                    DurationSeconds=duration_seconds,
                    SerialNumber=mfa_serial,
                    TokenCode=mfa_code,
                )["Credentials"]
                sts_creds["Expiration"] = sts_creds["Expiration"].isoformat()
            except Exception as e:
                # TODO
                message = str(e)
                raise click.ClickException(message)

        self.cache.write(sts_creds)
        return sts_creds

    def assume_role(
        self, profile: str, duration_seconds: int = ONE_HOUR_IN_SECONDS,
    ) -> Any:
        """Get the short-lived credentials from STS assume role.

        Arguments:
            profile: The profile that contains the `role_arn` and
                `source_profile` attributes.
            duration_seconds: The duration, in seconds, that the
                credentials should remain valid.

        Raises:
            ClickException: Failed to call `sts.assume_role()`

        Returns:
            Contains the response to a successful AssumeRole request,
            including temporary AWS credentials that can be used to make AWS
            requests.
        """
        session = boto3.Session(profile_name=self.bastion_sts, region_name=self.region)
        print("asdasdasdasdasdasda")
        print(dir(session.get_credentials))
        sts = session.client("sts")

        role_arn = self.credentials.get(profile, "role_arn")
        timestamp = pendulum.now().to_date_string()
        try:
            iam = session.client("iam")
            username = iam.get_user()["User"]["UserName"]
            role_session_name = f"{username}-{timestamp}"
        except Exception:
            role_session_name = f"bastion-assume-role-{timestamp}"

        try:
            sts_creds = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=duration_seconds,
            )["Credentials"]
        except Exception as e:
            # TODO
            message = str(e)
            raise click.ClickException(message)

        return sts_creds
