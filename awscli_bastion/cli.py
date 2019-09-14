from botocore.exceptions import ClientError
from datetime import timedelta
from .credentials import Credentials
from .cache import Cache
import boto3
import sys
import click
import getpass
import json


@click.group()
@click.version_option()
def main():
    """ bastion extends the awscli by managing mfa protected short-lived credentials. """
    return 0


@click.command()
@click.option("--duration-seconds", help="The duration, in seconds, that the credentials should remain valid.", default=timedelta(hours=12).seconds)
@click.option("--mfa-serial", help="The identification number of the MFA device that is associated with the IAM user.", default=None)
@click.option("--mfa-code", help="The value provided by the MFA device.", default=None)
@click.option("--bastion", help="The profile containing the long-lived IAM credentials.", default="bastion")
@click.option("--bastion-sts", help="The profile that assume role profiles source.", default="bastion-sts")
@click.option("--region", help="The region used when creating new AWS connections.", default="us-west-2")
def get_session_token(duration_seconds, mfa_serial, mfa_code,
    bastion, bastion_sts, region):
    """Output the bastion-sts short-lived credentials and output for the awscli credential_process.

    :param duration_seconds: The duration, in seconds, that the credentials should remain valid.
    :param mfa_serial: The identification number of the MFA device that is associated with the IAM user.
    :param mfa_code: The value provided by the MFA device.
    :param bastion: The profile containing the long-lived IAM credentials.
    :param bastion_sts: The profile that assume role profiles source.
    :param region: The region used when creating new AWS connections.
    :type duration_seconds: str
    :type mfa_serial: str
    :type mfa_code: str
    :type bastion: str
    :type bastion_sts: str
    :type region: str
    """

    credentials = Credentials()
    cache = Cache()
    creds = None

    if not mfa_serial:
        mfa_serial = credentials.get_mfa_serial(bastion_sts)

    if not mfa_code and not cache.is_expired():
        creds = cache.read()

    if not mfa_code and not creds:
        mfa_code = getpass.getpass("Enter MFA code for {}: ".format(mfa_serial))

    if not creds:
        session = boto3.Session(profile_name=bastion, region_name=region)
        sts = session.client("sts")
        creds = sts.get_session_token(
            DurationSeconds=duration_seconds,
            SerialNumber=mfa_serial,
            TokenCode=mfa_code
        )["Credentials"]
        cache.write(creds)

    # stdout for awscli credential_process
    click.echo(json.dumps(creds, indent=4))
    return None


@click.command()
def get_expiration_delta():
    """ Output how much time until the bastion-sts credentials expire. """
    cache = Cache()
    if cache.is_expired():
        click.echo("The bastion-sts credentials are expired.")
    else:
        d = cache.get_expiration(human_readable=True)
        click.echo("The bastion-sts credentials will expire {}.".format(d))
    return None


@click.command()
@click.argument("profile")
def set_default(profile):
    """ Set the default profile with attributes from another profile.

    :param profile str: The profile with a 'role_arn' attribute.
    :type profile: str
    """
    credentials = Credentials()
    credentials.set_default(profile)
    credentials.write()

    click.echo("Setting the default profile with attributes from the {} profile.".format(profile))
    return None


@click.command()
@click.option("--bastion-sts", help="the profile that assume role profiles will depend on.", default="bastion-sts")
def set_mfa_serial(bastion_sts):
    """ Set the 'mfa_serial' attribute for the bastion-sts profile.

    :param bastion_sts: The profile that assume role profiles source.
    :type bastion_sts: str
    :raises ValidationError: set-mfa-serial requires your iam user to have
                             'iam:get_user' and 'iam:list_mfa_devices' permissions.
    """
    try:
        iam = boto3.client('iam')
        username = iam.get_user()["User"]["UserName"]

        for iam_mfa_device in iam.list_mfa_devices(UserName=username)["MFADevices"]:
            mfa_serial = iam_mfa_device["SerialNumber"]
            break   # no need to check another MFA device.
        else:
            click.echo("Error: Failed to get mfa device from current iam user.")
            sys.exit(1)

    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            click.echo("Error: set-mfa-serial requires your iam user to have " \
                "'iam:get_user' and 'iam:list_mfa_devices' permissions.")
        else:
            click.echo("Unexpected error: {}".format(e))
        sys.exit(1)

    credentials = Credentials()
    credentials.set_mfa_serial(bastion_sts, mfa_serial)
    credentials.write()
    return None


@click.command()
def clear_cache():
    """ Clear the bastion-sts credential cache. """
    cache = Cache()
    cache.delete()
    return None


main.add_command(get_session_token)
main.add_command(get_expiration_delta)
main.add_command(set_default)
main.add_command(set_mfa_serial)
main.add_command(clear_cache)

if __name__ == "__main__":
    sys.exit(main())
