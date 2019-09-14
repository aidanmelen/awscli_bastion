from configparser import ConfigParser
import click
import pathlib
import sys


class Credentials:
    """ Manage getting and setting attributes for the aws shared credentials file. """

    def __init__(self):
        self.home = str(pathlib.Path.home())
        self.aws_shared_credentials_path = "{}/.aws/credentials".format(self.home)
        self.config = ConfigParser()
        self.config.read(self.aws_shared_credentials_path)

    def get_mfa_serial(self, bastion_sts):
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
    
    def set_mfa_serial(self, bastion_sts, mfa_serial):
        """ Set the 'mfa_serial' attribute for the given profile, typically the bastion-sts profile.

        :param bastion_sts: The profile that assume role profiles source.
        :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
        :type bastion_sts: str
        :type mfa_serial: str
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
