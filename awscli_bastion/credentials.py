from configparser import ConfigParser
from dateutil.tz import tzutc
from dateutil.parser import parse
import click
import datetime
import humanize
import pathlib
import sys


class Credentials:
    """ Manage getting and setting attributes for the aws shared credentials file. """

    def __init__(self):
        self.home = str(pathlib.Path.home())
        self.aws_shared_credentials_path = "{}/.aws/credentials".format(self.home)
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
            click.echo("The {} profile did not have the 'aws_session_expiration' attribute.")
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
            sys.exit(1)

    def set_mfa_serial(self, mfa_serial, bastion_sts="bastion_sts"):
        """ Set the 'mfa_serial' attribute for the given profile, typically the bastion-sts profile.

        :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
        :param bastion_sts: The profile that assume role profiles source.
        :type mfa_serial: str
        :type bastion_sts: str
        :raises Exception: Failed to set mfa_serial for bastion_sts profile.
        """
        try:
            self.config[bastion_sts]["mfa_serial"] = mfa_serial
        except Exception:
            click.echo("An error occured when setting the mfa_serial for {} profile.".format(bastion_sts))
            sys.exit(1)

    def set_default(self, profile):
        """ Set the default profile with attributes from another profile.

        :param profile: The profile with a 'role_arn' attribute.
        :type profile: str
        """
        self.config['default'] = dict(self.config[profile])

    def write(self):
        """ Write credentials to the aws shared credentials file. """
        with open(self.aws_shared_credentials_path, 'w') as f:
            self.config.write(f)
