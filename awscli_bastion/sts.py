from botocore.exceptions import ClientError
from datetime import timedelta
from dateutil.tz import tzutc
import boto3
import click
import datetime
import getpass
import sys


ONE_HOUR_IN_SECONDS = timedelta(hours=1).seconds
TWELVE_HOURS_IN_SECONDS = timedelta(hours=12).seconds

class STS:
    """ A small class that wraps relevant boto3 sts function calls. """

    def __init__(self, bastion="bastion", bastion_sts="bastion-sts", region="us-west-2",
        credentials=None, cache=None):
        self.bastion = bastion
        self.bastion_sts = bastion_sts
        self.region = region
        self.credentials = credentials
        self.cache = cache

    def is_mfa_code_invalid(self, mfa_code):
        return len(mfa_code) != 6 or not mfa_code.isdigit()
    
    def _get_mfa_code(self, mfa_serial):
        """ Prompt the user for the mfa code and return it.

        :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
        :type mfa_serial: str
        :return: 6 digit mfa code
        :rtype: str
        """
        is_mfa_code_invalid = True
        while is_mfa_code_invalid:
            mfa_code = getpass.getpass("Enter MFA code for {}: ".format(mfa_serial))
            is_mfa_code_invalid = self.is_mfa_code_invalid(mfa_code)
            if is_mfa_code_invalid:
                click.echo("Warning: The MFA code must be 6 digits. For example: 123456")
        return mfa_code

    def get_session_token(self, mfa_code=None, mfa_serial=None,
        duration_seconds=TWELVE_HOURS_IN_SECONDS):
        """ Get the short-lived credentials from sts.get_session_token()
         if the 'mfa_code' is provided. Otherwise, try to look up sts credentials from the cache.

        :param mfa_code: The value provided by the MFA device.
        :type mfa_code: str
        :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
        :type mfa_serial: str
        :param duration_seconds: The duration, in seconds, that the credentials should remain valid.
        :type duration_seconds: str
        :return: sts credentials
        :rtype: dict
        """
        if not mfa_serial:
            mfa_serial = self.credentials.get_mfa_serial(bastion_sts=self.bastion_sts)

        cached_sts_creds = None
        if not mfa_code and not self.cache.is_expired():
            cached_sts_creds = self.cache.read()

        if cached_sts_creds:
            sts_creds = cached_sts_creds
        else:
            if not mfa_code or self.is_mfa_code_invalid(mfa_code):
                mfa_code = self._get_mfa_code(mfa_serial)

            session = boto3.Session(profile_name=self.bastion, region_name=self.region)
            sts = session.client("sts")
            try:
                sts_creds = sts.get_session_token(
                    DurationSeconds=duration_seconds,
                    SerialNumber=mfa_serial,
                    TokenCode=mfa_code
                )["Credentials"]
                sts_creds["Expiration"] = sts_creds["Expiration"].isoformat()

            except Exception as e:
                click.echo(e)
                sys.exit(1)

        self.cache.write(sts_creds)
        return sts_creds

    def assume_role(self, profile, duration_seconds=ONE_HOUR_IN_SECONDS):
        """Get the short-lived credentials from sts.assume_role().

        :param profile: The profile that contains the 'role_arn' and 'source_profile' attributes.
        :type profile: str
        :param duration_seconds: The duration, in seconds, that the credentials should remain valid.
        :type duration_seconds: str
        :return: sts credentials
        :rtype: dict
        """
        session = boto3.Session(profile_name=self.bastion_sts, region_name=self.region)
        sts = session.client("sts")

        try:
            role_arn = self.credentials.config[profile]["role_arn"]
        except Exception:
            click.echo("An error occured when getting the role_arn from '{}' profile.".format(profile))
            sys.exit(1)
        
        timestamp = datetime.datetime.now(tzutc()).strftime("%Y-%m-%d")
        try:
            iam = boto3.client('iam')
            username = iam.get_user()["User"]["UserName"]
            role_session_name = "{}-{}".format(username, timestamp)
        except Exception:
            role_session_name = "bastion-assume-role-{}".format(timestamp)

        try:
            sts_creds = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=duration_seconds
            )["Credentials"]
        except ClientError as e:
            click.echo(e)
            sys.exit(1)
        
        return sts_creds
