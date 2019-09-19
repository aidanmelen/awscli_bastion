""" Manage the command line interface. """


from datetime import timedelta
from .credentials import Credentials
from .cache import Cache
from .sts import STS
from .rotate import Rotate
import sys
import click
import humanize
import json
import time


@click.group()
@click.version_option()
def main():
    """ The main entry point for the cli. """
    return 0


@click.command()
@click.option("--duration-seconds", help="The duration, in seconds, that the credentials should remain valid.", default=timedelta(hours=12).seconds)
@click.option("--mfa-serial", help="The identification number of the MFA device that is associated with the IAM user.", default=None)
@click.option("--mfa-code", help="The value provided by the MFA device.", default=None)
@click.option("--bastion", help="The profile containing the long-lived IAM credentials.", default="bastion")
@click.option("--bastion-sts", help="The profile that assume role profiles source.", default="bastion-sts")
@click.option("--region", help="The region used when creating new AWS connections.", default="us-west-2")
@click.option('--write-to-aws-shared-credentials-file', is_flag=True)
def get_session_token(duration_seconds, mfa_serial, mfa_code,
    bastion, bastion_sts, region, write_to_aws_shared_credentials_file):
    """Output the bastion-sts short-lived credentials from sts.get_session_token(). """
    credentials = Credentials()
    cache = Cache()
    sts = STS(
        bastion=bastion,
        bastion_sts=bastion_sts,
        region=region,
        credentials=credentials,
        cache=cache
    )
    sts_creds = sts.get_session_token(mfa_code=mfa_code, mfa_serial=mfa_serial, duration_seconds=duration_seconds)

    if write_to_aws_shared_credentials_file:
        credentials.config[bastion_sts]["aws_access_key_id"] = sts_creds["AccessKeyId"]
        credentials.config[bastion_sts]["aws_secret_access_key"] = sts_creds["SecretAccessKey"]
        credentials.config[bastion_sts]["aws_session_token"] = sts_creds["SessionToken"]
        credentials.config[bastion_sts]["aws_session_expiration"] = sts_creds["Expiration"]
        credentials.write()
        click.echo("Setting the '{}' profile with sts get session token credentials.".format(bastion_sts))
    else:
        # stdout for awscli credential_process
        click.echo(json.dumps(sts_creds, indent=4))

    return None


@click.command()
@click.argument("profile")
@click.option("--duration-seconds", help="The duration, in seconds, that the credentials should remain valid.", default=timedelta(hours=1).seconds)
@click.option("--repeat-seconds", help="The duration, in seconds, until assume_role will renew credentials.", default=0)
@click.option("--repeat-number", help="The number of repeated times assume_role will be called.", default=1)
@click.option("--bastion-sts", help="The profile that assume role profiles source.", default="bastion-sts")
@click.option("--region", help="The region used when creating new AWS connections.", default="us-west-2")
def assume_role(profile, duration_seconds, repeat_seconds, repeat_number, bastion_sts, region):
    """Set the profile with short-lived credentials from sts.assume_role(). """
    credentials = Credentials()

    is_repeating = repeat_seconds and repeat_number
    if is_repeating:
        humanized_repeat_duration = humanize.naturaldelta(repeat_seconds)
        humanized_repeat_number = "{} {}".format(repeat_number, "time" if repeat_number == 1 else "times")
        print("Setting the '{}' profile with sts assume role credentials every {} and will repeat {}.".format(
            profile, humanized_repeat_duration, humanized_repeat_number))

    repeat_iter = 0
    while repeat_iter < repeat_number:
        sts = STS(
            bastion_sts=bastion_sts,
            region=region,
            credentials=credentials
        )
        sts_creds = sts.assume_role(profile, duration_seconds=duration_seconds)

        credentials.config[profile]["aws_access_key_id"] = sts_creds["AccessKeyId"]
        credentials.config[profile]["aws_secret_access_key"] = sts_creds["SecretAccessKey"]
        credentials.config[profile]["aws_session_token"] = sts_creds["SessionToken"]
        credentials.config[profile]["aws_session_expiration"] = sts_creds["Expiration"].isoformat()
        credentials.write()

        if not is_repeating:
            click.echo("Setting the '{}' profile with sts assume role credentials.".format(profile))

        repeat_iter+=1
        if is_repeating:
            time.sleep(repeat_seconds)

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
    credentials = Credentials()
    credentials.set_mfa_serial(bastion_sts)
    credentials.write()

    click.echo("Setting the 'mfa_set' attribute for the '{}' profile.".format(bastion_sts))
    return None


@click.command()
@click.option("--bastion-sts", help="the profile that assume role profiles will depend on.", default="bastion-sts")
def get_expiration(bastion_sts):
    """ Output how much time until the bastion-sts credentials expire. """
    cache = Cache()
    if cache.is_expired():
        click.echo("The bastion-sts cached credentials are expired.")
    else:
        delta = cache.get_expiration()
        click.echo("The bastion-sts cached credentials will expire {}.".format(delta))
    return None


@click.command()
@click.option("--username", help="The username whos long-lived access key will be rotated.", default=None)
@click.option('--deactivate', help="Whether or not to deactivate the access key. Otherwise, it will be deleted during rotation.", is_flag=True)
@click.option("--bastion", help="The profile containing the long-lived IAM credentials.", default="bastion")
@click.option("--bastion-sts", help="The profile that assume role profiles will depend on.", default="bastion-sts")
@click.option("--region", help="The region used when creating new AWS connections.", default="us-west-2")
def rotate_access_keys(username, deactivate, bastion, bastion_sts, region):
    """ Rotate the bastion long-lived access key id and secret access keys. """

    credentials = Credentials()
    rotate = Rotate(
        username=username, deactivate=deactivate,
        bastion=bastion, bastion_sts=bastion_sts,
        region=region, credentials=credentials
    )
    rotate.rotate()


@click.command()
@click.option("--bastion", help="The profile containing the long-lived IAM credentials.", default="bastion")
def clear_cache(bastion):
    """ Clear the bastion-sts credential cache and sts credentials from the aws shared credentials file. """
    click.echo("Clearing the bastion-sts credential cache:")
    cache = Cache()
    cache.delete()

    click.echo("")

    click.echo("Clearing sts credentials from the aws shared credentials file:")
    credentials = Credentials()
    credentials.clear()
    return None


main.add_command(get_session_token)
main.add_command(assume_role)
main.add_command(set_default)
main.add_command(set_mfa_serial)
main.add_command(get_expiration)
main.add_command(rotate_access_keys)
main.add_command(clear_cache)

if __name__ == "__main__":
    sys.exit(main())
