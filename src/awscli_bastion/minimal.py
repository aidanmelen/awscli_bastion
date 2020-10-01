"""AWSCLI Bastion minimal module.

If you are like me, you do not trust open-source tools and libraries to handle
admin credentials for your aws accounts. awscli_bastion/minimal.py is written
as a script that offers minimal bastion functionality. It is intended to be
quick and easy to understand. A minimal number of python libraries are used to
reduce security risks.
"""
import configparser
import datetime
import os
import pathlib
import sys

import boto3


NAME: str = os.path.basename(os.path.realpath(__file__))
BASTION: str = "bastion"
BASTION_STS: str = "bastion-sts"
AWS_SHARED_CREDENTIAL_FILE: str = "{}/.aws/credentials".format(pathlib.Path.home())
token_code: int = -1


def main() -> None:
    """AWSCLI Bastion minimal."""
    # Parse arguments
    args = sys.argv[1:]
    if len(args) == 0:
        print(f"python {NAME} ASSUME_ROLE_PROFILE TOKEN_CODE")
        print(f"python {NAME} dev-admin 123456")
        print(f"python {NAME} dev-admin")
        sys.exit(1)
    if len(args) >= 1:
        assume_role_profile = args[0]
    if len(args) >= 2:
        token_code = int(args[1])

    # Read AWS_SHARED_CREDENTIAL_FILE
    config = configparser.ConfigParser()
    config.read(AWS_SHARED_CREDENTIAL_FILE)

    # STS get session token
    if token_code:
        try:
            bastion_client = boto3.Session(profile_name=BASTION).client("sts")

            twelve_hours_in_seconds = 43200
            serial_number = config[BASTION_STS]["mfa_serial"]

            sts_get_session_token_creds = bastion_client.get_session_token(
                DurationSeconds=twelve_hours_in_seconds,
                SerialNumber=serial_number,
                TokenCode=token_code,
            )["Credentials"]

            config[BASTION_STS]["aws_access_key_id"] = sts_get_session_token_creds[
                "AccessKeyId"
            ]
            config[BASTION_STS]["aws_secret_access_key"] = sts_get_session_token_creds[
                "SecretAccessKey"
            ]
            config[BASTION_STS]["aws_session_token"] = sts_get_session_token_creds[
                "SessionToken"
            ]

            with open(AWS_SHARED_CREDENTIAL_FILE, "w") as f:
                config.write(f)
            print(
                f"Setting the '{BASTION_STS}' profile with sts get session "
                "token credentials."
            )
        except Exception:
            print(
                f"Failed to set the '{BASTION_STS}' profile with sts get "
                "session token credentials."
            )
            sys.exit(1)
    elif "aws_session_token" not in config[BASTION_STS]:
        print(
            "An MFA token code is required when setting bastion-sts for the "
            "first time."
        )
        sys.exit(1)

    # STS assume role
    try:
        bastion_sts_client = boto3.Session(profile_name=BASTION_STS).client("sts")

        now = str(datetime.datetime.now()).replace(" ", "_")
        one_hour_in_seconds = 3600
        role_arn = config[assume_role_profile]["role_arn"]
        role_session_name = f"bastion-assume-role-{now}"

        sts_assume_role_creds = bastion_sts_client.assume_role(
            DurationSeconds=one_hour_in_seconds,
            RoleArn=role_arn,
            RoleSessionName=role_session_name,
        )["Credentials"]

        config[assume_role_profile]["aws_access_key_id"] = sts_assume_role_creds[
            "AccessKeyId"
        ]
        config[assume_role_profile]["aws_secret_access_key"] = sts_assume_role_creds[
            "SecretAccessKey"
        ]
        config[assume_role_profile]["aws_session_token"] = sts_assume_role_creds[
            "SessionToken"
        ]

        with open(AWS_SHARED_CREDENTIAL_FILE, "w") as f:
            config.write(f)
        print(
            "Setting the '{assume_role_profile}' profile with sts assume role "
            "credentials."
        )
    except Exception:
        print(
            "Failed to set the '{assume_role_profile}' profile with sts assume "
            "role credentials."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
