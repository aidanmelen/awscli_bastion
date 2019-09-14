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
    def __init__(self):
        self.home = str(pathlib.Path.home())
        self.bastion_cache_path = "{}/.aws/cli/cache/bastion.json".format(self.home)

    def does_exist(self):
        return isfile(self.bastion_cache_path)

    def is_expired(self):
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
        now_dt = datetime.datetime.now(tzutc())
        expiration_iso = self.read()["Expiration"]
        expiration_dt = parse(expiration_iso)
        delta = now_dt - expiration_dt
        return humanize.naturaltime(delta) if human_readable else delta

    def write(self, creds):
        creds["Version"] = 1
        creds["Expiration"] = creds["Expiration"].isoformat()
        with open(self.bastion_cache_path, 'w+') as f:
            json.dump(creds, f, indent=4)

    def read(self):
        with open(self.bastion_cache_path, 'r') as f:
            return json.load(f)

    def delete(self):
        os.remove(self.bastion_cache_path)
