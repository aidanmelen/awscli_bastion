from botocore.exceptions import ClientError
from datetime import timedelta
from dateutil.tz import tzutc
from .credentials import Credentials
from .cache import Cache
import boto3
import datetime
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
@click.option('--write-to-shared-credentials-file', is_flag=True)
def get_session_token(duration_seconds, mfa_serial, mfa_code,
    bastion, bastion_sts, region, write_to_shared_credentials_file):
    """Output the bastion-sts short-lived credentials and output for the awscli credential_process. """
    credentials = Credentials()
    cache = Cache()
    sts_creds = None

    if not mfa_serial:
        mfa_serial = credentials.get_mfa_serial(bastion_sts)

    if not mfa_code and not cache.is_expired():
        sts_creds = cache.read()

    if not mfa_code and not sts_creds:
        mfa_code = getpass.getpass("Enter MFA code for {}: ".format(mfa_serial))

    if not sts_creds:
        session = boto3.Session(profile_name=bastion, region_name=region)
        sts = session.client("sts")
        try:
            sts_creds = sts.get_session_token(
                DurationSeconds=duration_seconds,
                SerialNumber=mfa_serial,
                TokenCode=mfa_code
            )["Credentials"]
            sts_creds["Expiration"] = sts_creds["Expiration"].isoformat()
            cache.write(sts_creds)

        except ClientError as e:
            click.echo(e)
            sys.exit(1)

    if write_to_shared_credentials_file:
        credentials.config[bastion_sts]["aws_access_key_id"] = sts_creds["AccessKeyId"]
        credentials.config[bastion_sts]["aws_secret_access_key"] = sts_creds["SecretAccessKey"]
        credentials.config[bastion_sts]["aws_session_token"] = sts_creds["SessionToken"]
        credentials.config[bastion_sts]["aws_session_expiration"] = sts_creds["Expiration"]
        credentials.write()
        click.echo("Setting the '{}' profile with sts credential attributes.".format(bastion_sts))
    else:
        # stdout for awscli credential_process
        click.echo(json.dumps(sts_creds, indent=4))
    return None


@click.command()
@click.argument("profile")
@click.option("--duration-seconds", help="The duration, in seconds, that the credentials should remain valid.", default=timedelta(hours=1).seconds)
@click.option("--bastion-sts", help="The profile that assume role profiles source.", default="bastion-sts")
@click.option("--region", help="The region used when creating new AWS connections.", default="us-west-2")
def assume_role(profile, duration_seconds, bastion_sts, region):
    """Set the profile with short-lived credentials from assume_role. """
    credentials = Credentials()
    session = boto3.Session(profile_name=bastion_sts, region_name=region)
    sts = session.client("sts")

    sts_creds = sts.assume_role(
        RoleArn=credentials.config[profile]["role_arn"],
        RoleSessionName="bastion-assume-role-{}".format(datetime.datetime.now(tzutc()).strftime("%Y-%m-%d")),
        DurationSeconds=duration_seconds
    )["Credentials"]

    credentials.config[profile]["aws_access_key_id"] = sts_creds["AccessKeyId"]
    credentials.config[profile]["aws_secret_access_key"] = sts_creds["SecretAccessKey"]
    credentials.config[profile]["aws_session_token"] = sts_creds["SessionToken"]
    credentials.config[profile]["aws_session_expiration"] = sts_creds["Expiration"].isoformat()
    credentials.write()

    click.echo("Setting the '{}' profile with assume role sts credential attributes.".format(profile))
    return None


@click.command()
@click.option("--bastion-sts", help="the profile that assume role profiles will depend on.", default="bastion-sts")
def get_expiration(bastion_sts):
    """ Output how much time until the bastion-sts credentials expire. """
    credentials = Credentials()
    cache = Cache()

    if "aws_session_token" in credentials.config[bastion_sts]:
        click.echo("Checking '{}' for expiration timestamp.".format(credentials.aws_shared_credentials_path))
        if credentials.is_expired():
            click.echo("The bastion-sts credentials are expired.")
        else:
            delta = credentials.get_expiration()
            click.echo("The bastion-sts credentials will expire {}.".format(delta))
    else:
        click.echo("Checking '{}' for expiration timestamp.".format(cache.bastion_sts_cache_path))
        if cache.is_expired():
            click.echo("The bastion-sts cached credentials are expired.")
        else:
            delta = cache.get_expiration()
            click.echo("The bastion-sts cached credentials will expire {}.".format(delta))
    return None


@click.command()
@click.argument("profile")
def set_default(profile):
    """ Set the default profile with attributes from another profile. """
    credentials = Credentials()
    credentials.set_default(profile)
    credentials.write()

    click.echo("Setting the 'default' profile with attributes from the '{}' profile.".format(profile))
    return None


@click.command()
@click.option("--bastion-sts", help="the profile that assume role profiles will depend on.", default="bastion-sts")
def set_mfa_serial(bastion_sts):
    """ Set the 'mfa_serial' attribute for the bastion-sts profile. """
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

    credentials = Credentials()
    credentials.set_mfa_serial(bastion_sts, mfa_serial)
    credentials.write()

    click.echo("Setting the 'mfa_set' attribute for the '{}' profile.".format(bastion_sts))
    return None


@click.command()
@click.option("--bastion", help="The profile containing the long-lived IAM credentials.", default="bastion")
def clear_cache(bastion):
    """ Clear the bastion-sts credential cache. """
    cache = Cache()
    cache_path = cache.bastion_sts_cache_path
    cache.delete()
    click.echo("{} has been removed.".format(cache_path))

    credentials = Credentials()
    profiles = credentials.config.sections()
    profiles.remove(bastion) # we don't want to remove the long-lived credentials
    for profile in profiles:
        if "aws_access_key_id" in credentials.config[profile]:
            del credentials.config[profile]["aws_access_key_id"]
        if "aws_secret_access_key" in credentials.config[profile]:
            del credentials.config[profile]["aws_secret_access_key"]
        if "aws_session_token" in credentials.config[profile]:
            del credentials.config[profile]["aws_session_token"]
        click.echo("sts credentials were removed from the {} profile.".format(profile))
    credentials.write()
    return None


main.add_command(get_session_token)
main.add_command(assume_role)
main.add_command(get_expiration)
main.add_command(set_default)
main.add_command(set_mfa_serial)
main.add_command(clear_cache)

if __name__ == "__main__":
    sys.exit(main())
