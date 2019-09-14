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
    return 0


@click.command()
@click.option("--duration-seconds", help="The duration, in seconds, that the credentials should remain valid.", default=timedelta(hours=12).seconds)
@click.option("--mfa-serial", help="the identification number of the MFA device that is associated with the IAM user.", default=None)
@click.option("--mfa-code", help="the value provided by the MFA device.", default=None)
@click.option("--profile", help="the profile containing the long-lived IAM credentials.", default="bastion")
@click.option("--profile-sts", help="the profile that assume role profiles will depend on.", default="bastion-sts")
@click.option("--region", help="the region used when creating new AWS connections.", default="us-west-2")
def get_session_token(duration_seconds, mfa_serial, mfa_code,
    profile, profile_sts, region):

    credentials = Credentials()
    cache = Cache()
    creds = None

    if not mfa_serial:
        mfa_serial = credentials.get_mfa_serial(profile_sts)

    if not mfa_code and not cache.is_expired():
        creds = cache.read()

    if not mfa_code and not creds:
        mfa_code = getpass.getpass("Enter MFA code for {}: ".format(mfa_serial))

    if not creds:
        session = boto3.Session(profile_name=profile, region_name=region)
        sts = session.client("sts")
        creds = sts.get_session_token(
            DurationSeconds=duration_seconds,
            SerialNumber=mfa_serial,
            TokenCode=mfa_code
        )["Credentials"]
        cache.write(creds)

    click.echo(json.dumps(creds, indent=4))
    return None


@click.command()
@click.argument("profile")
def set_default(profile):
    credentials = Credentials()
    credentials.update_default(profile)
    credentials.write()

    click.echo("updating the default profile with the {} profile".format(profile))
    return None


@click.command()
def reset_cache():
    cache = Cache()
    cache.delete()


@click.command()
def get_expiration_delta():
    cache = Cache()
    if cache.is_expired():
        click.echo("the bastion credentials are expired.")
    else:
        d = cache.get_expiration(human_readable=True)
        click.echo("The bastion credentials will expire {}.".format(d))


main.add_command(get_session_token)
main.add_command(set_default)
main.add_command(reset_cache)
main.add_command(get_expiration_delta)

if __name__ == "__main__":
    sys.exit(main())
