from datetime import timedelta
from dateutil.tz import tzutc
from dateutil.parser import parse
from os.path import isfile
import datetime
import humanize
import json
import os
import pathlib


class Cache:
    """ Manage the bastion-sts credential cache (~/.aws/cli/cache/bastion-sts.json). """

    def __init__(self):
        self.home = str(pathlib.Path.home())
        self.bastion_sts_cache_path = "{}/.aws/cli/cache/bastion-sts.json".format(self.home)

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
        now_dt = datetime.datetime.now(tzutc())
        expiration_iso = self.read()["Expiration"]
        expiration_dt = parse(expiration_iso)
        delta = now_dt - expiration_dt
        return humanize.naturaltime(delta) if human_readable else delta

    def write(self, creds):
        """ Writes json formatted credentials to the bastion-sts cache file.

        :param creds: bastion-sts short-lived credentials.
        :type creds: bool
        :type creds: dict
        """
        creds["Version"] = 1
        creds["Expiration"] = creds["Expiration"].isoformat()
        with open(self.bastion_sts_cache_path, 'w+') as f:
            json.dump(creds, f, indent=4)

    def read(self):
        """ Reads json formatted credentials to the bastion-sts cache file. """
        with open(self.bastion_sts_cache_path, 'r') as f:
            return json.load(f)

    def delete(self):
        """ Deletes the bastion-sts cache file. """
        os.remove(self.bastion_sts_cache_path)
