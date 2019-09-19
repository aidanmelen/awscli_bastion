from botocore.exceptions import ClientError
from configparser import ConfigParser
from dateutil.tz import tzutc
from dateutil.parser import parse
import boto3
import click
import datetime
import humanize
import pathlib
import os
import sys


class Credentials:
    """ Manage getting and setting attributes for the aws shared credentials file. """

    def __init__(self):
        self.aws_shared_credentials_path = os.path.join(pathlib.Path.home(), ".aws/credentials")
        self.config = ConfigParser()
        self.config.read(self.aws_shared_credentials_path)

    def is_expired(self, bastion_sts="bastion-sts"):
        """ Return whether or not the bastion-sts credentials are expired.

        :return: Whether or not the bastion-sts credentials are expired.
        :rtype: bool
        """
        expired = False
        now_dt = datetime.datetime.now(tzutc())
        expiration_iso = self.config[bastion_sts]["aws_session_expiration"]
        expiration_dt = parse(expiration_iso)
        if now_dt > expiration_dt:
            expired = True
        return expired

    def get_expiration(self, profile="bastion-sts", human_readable=True):
        """ Return how much time until the bastion-sts credentials expire.

        :param human_readable: Whether or not to output as human readable.
        :type human_readable: bool
        :return: How much time until the bastion-sts credentials expire.
        :rtype: str
        """
        try:
            expiration_iso = self.config[profile]["aws_session_expiration"]
        except KeyError:
            click.echo("The '{}' profile did not have the 'aws_session_expiration' attribute.")
            sys.exit(1)

        now_dt = datetime.datetime.now(tzutc())
        expiration_dt = parse(expiration_iso)
        delta = now_dt - expiration_dt
        return humanize.naturaltime(delta) if human_readable else delta

    def get_mfa_serial(self, bastion_sts="bastion-sts"):
        """ Get the mfa serial number for the bastion iam user.

        :param bastion_sts: The profile containing the 'mfa_serial' attribute.
        :type bastion_sts: str
        :raises Exception: Failed to get mfa_serial from bastion_sts profile.
        :return: The identification number of the MFA device that is associated with the bastion_sts profile.
        """
        try:
            return self.config[bastion_sts]["mfa_serial"]
        except Exception:
            click.echo("An error occured when getting the mfa_serial from {} profile.".format(bastion_sts))
            click.echo("Try setting mfa_serial attribute with the 'bastion set-mfa-serial' command.")
            sys.exit(1)

    def set_mfa_serial(self, mfa_serial=None, bastion_sts="bastion_sts"):
        """ Set the 'mfa_serial' attribute for the given profile, typically the bastion-sts profile.

        :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
        :param bastion_sts: The profile that assume role profiles source.
        :type mfa_serial: str
        :type bastion_sts: str
        :raises ClientError: Failed to get mfa_serial from the iam user.
        :raises Exception: Failed to set mfa_serial for bastion_sts profile.
        """
        if not mfa_serial:
            try:
                iam = boto3.client('iam')
                username = iam.get_user()["User"]["UserName"]

                for iam_mfa_device in iam.list_mfa_devices(UserName=username)["MFADevices"]:
                    mfa_serial = iam_mfa_device["SerialNumber"]
                    break   # no need to check another MFA device.
                else:
                    click.echo("An error occured when getting the mfa device from current iam user.")
                    sys.exit(1)

            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationError':
                    click.echo("An error occured when getting the mfa serial number. " \
                        "Your iam user to have 'iam:get_user' and 'iam:list_mfa_devices' " \
                        "permissions. \n{}".format(e))
                else:
                    click.echo("Unexpected error: {}".format(e))
                sys.exit(1)
        
        self.config[bastion_sts]["mfa_serial"] = mfa_serial

    def set_default(self, profile):
        """ Set the default profile with attributes from another profile.

        :param profile: The profile with a 'role_arn' attribute.
        :type profile: str
        """
        try:            
            self.config['default'] = dict(self.config[profile])
        except KeyError:
            click.echo("Failed to set default profile with attributes from '{}' profile".format(profile))
            click.echo("The '{}' profile is not defined in the {} file.".format(profile, self.aws_shared_credentials_path))
            sys.exit(1)
    
    def clear(self, bastion="bastion"):
        """ Clear sts credentials from the aws shared credentials file.

        :param bastion: The profile containing the long-lived IAM credentials.
        :type bastion: str
        :return: Whether or not any sts credentials were removed from the aws shared credentials file.
        :rtype: bool
        """
        profiles = self.config.sections()

        # we don't want to remove the long-lived credentials
        profiles.remove(bastion)

        click.echo("- Skipping the '{}' profile because it may contain long-lived credentials.".format(bastion))

        for profile in profiles:
            if "source_profile" not in self.config[profile]:
                click.echo("- Skipping the '{}' profile because it may contain long-lived credentials.".format(profile))
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
                click.echo("- STS credentials were removed from the {} profile.".format(profile))
        self.write()

    def write(self):
        """ Write credentials to the aws shared credentials file. """
        with open(self.aws_shared_credentials_path, 'w') as f:
            self.config.write(f)
