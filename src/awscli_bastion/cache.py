"""AWSCLI Bastion session cache module."""
import json
import logging
import os
import pathlib
from typing import Any

import click
import pendulum


logger = logging.getLogger(__name__)


class Cache:
    """AWSCLI Bastion session cache module."""

    def __init__(self) -> None:
        """Cache init."""
        self.bastion_sts_cache_file = os.environ.get(
            "AWSCLI_BASTION_STS_CACHE_FILE",
            os.path.join(pathlib.Path.home(), ".aws/cli/cache/bastion-sts.json"),
        )
        self.aws_shared_cache_dir = os.path.dirname(self.bastion_sts_cache_file)

        if not os.path.isdir(self.aws_shared_cache_dir):
            os.makedirs(self.aws_shared_cache_dir)

    def is_expired(self) -> bool:
        """Return whether or not the bastion-sts credentials are expired.

        Returns:
            If the bastion-sts credentials are expired.
        """
        now_dt = pendulum.now()  # type: ignore
        expiration_iso = self.read()["Expiration"]
        expiration_dt = pendulum.parse(expiration_iso)  # type: ignore
        return bool(now_dt > expiration_dt)

    def get_expiration(self, in_words: bool = True) -> Any:
        """Return how much time until the bastion-sts credentials expire.

        Arguments:
            in_words: Output as human readable.

        Raises:
            ClickException: Failed to get the expiration from cache.

        Returns:
            How much time until the bastion-sts credentials expire.
        """
        cache = self.read()
        if "Expiration" in cache:
            expiration_iso = self.read()["Expiration"]
        else:
            raise click.ClickException("Failed to get cached bastion-sts expiration.")

        now_dt = pendulum.now()  # type: ignore
        expiration_dt = pendulum.parse(expiration_iso)  # type: ignore
        period = now_dt - expiration_dt
        return period.in_words() if in_words else period

    def write(self, creds: Any) -> None:
        """Writes json formatted credentials to the bastion-sts cache file.

        Arguments:
            creds: bastion-sts short-lived credentials.
        """
        with open(self.bastion_sts_cache_file, "w+") as f:
            creds["Version"] = 1
            json.dump(creds, f, indent=4)

    def read(self) -> Any:
        """Read the bastion-sts cache file.

        Returns:
            bastion-sts cache file contents.
        """
        with open(self.bastion_sts_cache_file, "r") as f:
            return json.load(f)

    def delete(self) -> None:
        """Deletes the cache files in the aws shared cache directory."""
        cache_files = os.listdir(self.aws_shared_cache_dir)
        if cache_files:
            for cache in os.listdir(self.aws_shared_cache_dir):
                os.remove(os.path.join(self.aws_shared_cache_dir, cache))
                click.echo("- Deleted the '{}' file.".format(cache))
        else:
            click.echo("- No cache files to delete.")
