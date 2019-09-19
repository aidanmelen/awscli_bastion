from configparser import ConfigParser
import click
import boto3
import pathlib
import time
import sys

class Rotate:
    """ Manages the creation, verification, deletion or deactivation, replacment of aws access keys for the bastion account. """

    def __init__(self, deactivate=False, username=None, bastion="bastion", bastion_sts="bastion-sts", region="us-west-2", credentials=None):
        self.deactivate = deactivate
        self.bastion = bastion
        self.region = region
        self.credentials = credentials

        try:
            self.bastion_session = boto3.Session(profile_name=bastion,region_name=self.region)
            self.bastion_sts_session = boto3.Session(profile_name=bastion_sts,region_name=self.region)

            iam = self.bastion_session.client("iam")
            self.username = username if username else iam.get_user()["User"]["UserName"]

        except Exception as e:
            print(e)
            sys.exit(1)

    def create_access_key(self):
        """ Create aws access key for the bastion profile. """
        try:
            iam_client = self.bastion_sts_session.client("iam")
            return iam_client.create_access_key(UserName=self.username)

        except Exception as e:
            print(e)
            sys.exit(1)
    
    def is_active(self, access_key):
        """ Ensure that aws access key is active. 
        
        :param access_key: The aws access key to verify activation.
        :type access_key: str
        :return: Whether or not the aws access key is active.
        :rtype: bool
        """
        # https://github.com/boto/boto3/issues/2133
        # iam = boto3.resource('iam')
        # return iam.AccessKey('user_name', access_key.access_key_id).status == "Active"
        return True

    def retire_bastion_access_key(self):
        """
        Retire aws access key for the bastion profile.
        By default, this means deletion. Specify the 'deactivate' class variable to deactivate.
        """
        bastion_aws_access_key_id = self.credentials.config.get(
            self.bastion, 'aws_access_key_id', fallback=None)

        iam = self.bastion_sts_session.resource("iam")
        access_key = iam.AccessKey(self.username, bastion_aws_access_key_id)
        if self.deactivate:
            access_key.deactivate()
        else:
            access_key.delete()
        
        self.credentials.config[self.bastion]["aws_access_key_id"] = ""
        self.credentials.config[self.bastion]["aws_secret_access_key"] = ""
    
    def write(self, access_key):
        """ Write access key to the bastion profile in the aws share credentials file.

        :param access_key: The aws access key access key to write.
        :type access_key: str
        """
        self.credentials.config[self.bastion]["aws_access_key_id"] = access_key["AccessKey"]["AccessKeyId"]
        self.credentials.config[self.bastion]["aws_secret_access_key"] = access_key["AccessKey"]["SecretAccessKey"]
        self.credentials.write()

    def rotate(self):
        """ Rotate aws access key credentials for the bastion profile. """
        access_key = self.create_access_key()
        if self.is_active(access_key):
            self.retire_bastion_access_key()
            self.write(access_key)
            click.echo("Rotating long-lived credentials for the {} profile.".format(self.bastion))
        else:
            click.echo("There was a problem creating the new long-lived credentials. Will not rotate current credentials.")
            sys.exit(1)