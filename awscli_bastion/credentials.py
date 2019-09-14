from configparser import ConfigParser
import pathlib
import sys


class Credentials:
    def __init__(self):
        self.home = str(pathlib.Path.home())
        self.aws_shared_credentials_path = "{}/.aws/credentials".format(self.home)
        self.config = ConfigParser()
        self.config.read(self.aws_shared_credentials_path)

    def get_mfa_serial(self, profile):
        try:
            return self.config[profile]["mfa_serial"]
        except Exception:
            print("failed to get mfa_serial from {} profile".format(profile))
            sys.exit(1)

    def update_default(self, profile):
        self.config['default'] = dict(self.config[profile])

    def write(self):
        with open(self.aws_shared_credentials_path, 'w') as f:
            self.config.write(f)
