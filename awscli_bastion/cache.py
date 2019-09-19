from dateutil.tz import tzutc
from dateutil.parser import parse
from os.path import isfile
import click
import datetime
import humanize
import json
import os
import pathlib
import sys


class Cache:
    """ Manage the bastion-sts credential cache (~/.aws/cli/cache/bastion-sts.json). """

    def __init__(self):
        self.aws_shared_cache_path = os.path.join(pathlib.Path.home(), ".aws/cli/cache")
        self.bastion_sts_cache_path = os.path.join(self.aws_shared_cache_path, "bastion-sts.json")

    def does_exist(self):
        """ Return whether or not the bastion-sts credential cache exists.

        :rtype: bool
        :return: Whether or not the bastion-sts credential cache exists.
        """
        return isfile(self.bastion_sts_cache_path)

    def is_expired(self):
        """ Return whether or not the bastion-sts credentials are expired.

        :return: Whether or not the bastion-sts credentials are expired.
        :rtype: bool
        """
        expired = False
        if self.does_exist():
            now_dt = datetime.datetime.now(tzutc())
            expiration_iso = self.read()["Expiration"]
            expiration_dt = parse(expiration_iso)
            if now_dt > expiration_dt:
                expired = True
        else:
            expired = True
        return expired

    def get_expiration(self, human_readable=True):
        """ Return how much time until the bastion-sts credentials expire.

        :param human_readable: Whether or not to output as human readable.
        :type human_readable: bool
        :return: How much time until the bastion-sts credentials expire.
        :rtype: str
        """
        try:
            expiration_iso = self.read()["Expiration"]
        except KeyError:
            click.echo("The {} profile did not have the 'aws_session_expiration' attribute.")
            sys.exit(1)

        expiration_dt = parse(expiration_iso)
        now_dt = datetime.datetime.now(tzutc())
        delta = now_dt - expiration_dt
        return humanize.naturaltime(delta) if human_readable else delta

    def write(self, creds):
        """ Writes json formatted credentials to the bastion-sts cache file.

        :param creds: bastion-sts short-lived credentials.
        :type creds: bool
        :type creds: dict
        """
        creds["Version"] = 1
        with open(self.bastion_sts_cache_path, 'w+') as f:
            json.dump(creds, f, indent=4)

    def read(self):
        """ Reads json formatted credentials to the bastion-sts cache file. """
        with open(self.bastion_sts_cache_path, 'r') as f:
            return json.load(f)

    def delete(self):
        """ Deletes the cache files in the aws shared cache directory.  """
        cache_files = os.listdir(self.aws_shared_cache_path)
        if cache_files:
            for cache in os.listdir(self.aws_shared_cache_path):
                os.remove(os.path.join(self.aws_shared_cache_path, cache))
                click.echo("- Deleted the '{}' file.".format(cache))
        else:
            click.echo("- No cache files to delete.")