from datetime import tzinfo
from dateutil.tz import tzutc
from os.path import isfile

import datetime
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
        return True

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