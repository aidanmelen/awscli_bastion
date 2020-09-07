"""Command-line interface."""
import click
import pendulum

from . import __version__

# from . import auth
# from . import cache
# from . import credentials
# from . import rotate


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """AWSCLI Bastion."""
    pass


@click.command()
@click.option(
    "--duration-seconds",
    help="The duration, in seconds, that the credentials should remain valid.",
    default=pendulum.duration(hours=12).seconds,
    show_default=True,
)
@click.option(
    "--mfa-serial",
    help="The identification number of the MFA device that is associated with"
    "the IAM user.",
    default=None,
    show_default=True,
)
@click.option("--mfa-code", help="The value provided by the MFA device.", default=None)
@click.option(
    "--bastion",
    help="The profile containing the IAM user credentials.",
    default="bastion",
    show_default=True,
)
@click.option(
    "--bastion-sts",
    help="The profile that assume role profile's source.",
    default="bastion-sts",
    show_default=True,
)
@click.option(
    "--region",
    help="The region used when creating new AWS connections.",
    default="us-west-2",
    show_default=True,
)
@click.option("--write", is_flag=True, show_default=True)
def session_token(
    duration_seconds: int,
    mfa_serial: str,
    mfa_code: int,
    bastion: str,
    bastion_sts: str,
    region: str,
    write: bool,
) -> None:
    """Get bastion STS credentials."""
    pass


@click.command()
@click.argument("profile")
@click.option(
    "--duration-seconds",
    help="The duration, in seconds, that the credentials should remain valid.",
    default=pendulum.duration(hours=1).seconds,
    show_default=True,
)
@click.option(
    "--bastion-sts",
    help="The profile that assume role profile's source.",
    default="bastion-sts",
    show_default=True,
)
@click.option(
    "--region",
    help="The region used when creating new AWS connections.",
    default="us-west-2",
    show_default=True,
)
def assume_role(
    profile: str, duration_seconds: int, bastion_sts: str, region: str
) -> None:
    """Get assume role STS credentials."""
    pass


@click.command()
@click.argument("profile")
def set_default(profile: str) -> None:
    """Set the default profile with attributes from another profile."""
    pass


@click.command()
@click.option(
    "--bastion-sts",
    help="The profile that assume role profile's source.",
    default="bastion-sts",
    show_default=True,
)
def set_mfa_serial(bastion_sts: str) -> None:
    """Set the 'mfa_serial' attribute for the bastion-sts profile."""
    pass


@click.command()
@click.option(
    "--bastion-sts",
    help="The profile that assume role profile's source.",
    default="bastion-sts",
    show_default=True,
)
def show_expiration(bastion_sts: str) -> None:
    """Output how much time until the bastion-sts credentials expire."""
    pass


@click.command()
@click.option(
    "--username",
    help="The IAM username to  have access key be rotated.",
    default="",
    show_default=True,
)
@click.option(
    "--should-delete",
    help="Whether or not to delete the access key; otherwise, it will be "
    "deactivated during rotation.",
    is_flag=True,
    show_default=True,
)
@click.option(
    "--bastion",
    help="The profile containing the IAM user credentials.",
    default="bastion",
    show_default=True,
)
@click.option(
    "--bastion-sts",
    help="The profile that assume role profile's source.",
    default="bastion-sts",
    show_default=True,
)
@click.option(
    "--region",
    help="The region used when creating new AWS connections.",
    default="us-west-2",
    show_default=True,
)
def rotate(
    username: str, should_delete: bool, bastion: str, bastion_sts: str, region: str
) -> None:
    """Rotate AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY for IAM user."""
    pass


@click.command()
@click.option(
    "--bastion",
    help="The profile containing the IAM user credentials.",
    default="bastion",
    show_default=True,
)
def clear(bastion: str) -> None:
    """Clear STS in AWS_SHARED_CREDENTIALS_FILE and AWS_SHARED_CACHE_DIR."""
    pass


main.add_command(session_token)
main.add_command(assume_role)
main.add_command(set_default)
main.add_command(set_mfa_serial)
main.add_command(show_expiration)
main.add_command(rotate)
main.add_command(clear)


if __name__ == "__main__":
    main(prog_name="awscli-bastion")  # pragma: no cover
