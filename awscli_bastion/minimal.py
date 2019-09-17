"""
If you are like me, you do not trust open-source tools and libraries to handle admin
credentials for your aws accounts. awscli_bastion/minimal.py is written as a script that offers
minimal bastion functionality. It is intended to be quick and easy to understand.
A minimal number of python libraries are used to reduce security risks.
"""

import boto3
import configparser
import pathlib
import random
import sys


def main():
    ##############
    # Set defaults
    ##############
    bastion = "bastion"
    bastion_sts = "bastion-sts"
    aws_shared_credentials_path = "{}/.aws/credentials".format(pathlib.Path.home())
    token_code = None

    #################
    # Parse arguments
    #################
    args = sys.argv[1:]

    if len(args) == 0:
        print("python auth.py ASSUME_ROLE_PROFILE TOKEN_CODE")
        print("python auth.py dev-admin 123456")
        print("python auth.py dev-admin")
        sys.exit(1)
    if len(args) >= 1:
        assume_role_profile = args[0]
    if len(args) >= 2:
        token_code = args[1]

    ##################################
    # Read aws shared credentials file
    ##################################
    config = configparser.ConfigParser()
    config.read(aws_shared_credentials_path)

    #######################
    # STS get session token
    #######################
    if token_code:
        try:
            bastion_client = boto3.Session(profile_name=bastion).client("sts")

            twelve_hours_in_seconds = 43200
            serial_number = config[bastion_sts]["mfa_serial"]

            sts_get_session_token_creds = bastion_client.get_session_token(
                DurationSeconds=twelve_hours_in_seconds,
                SerialNumber=serial_number,
                TokenCode=token_code
            )["Credentials"]

            config[bastion_sts]["aws_access_key_id"] = sts_get_session_token_creds["AccessKeyId"]
            config[bastion_sts]["aws_secret_access_key"] = sts_get_session_token_creds["SecretAccessKey"]
            config[bastion_sts]["aws_session_token"] = sts_get_session_token_creds["SessionToken"]

            with open(aws_shared_credentials_path, 'w') as f:
                config.write(f)
            print("Setting the '{}' profile with sts get session token credentials.".format(bastion_sts))

        except Exception:
            print("Failed to set the '{}' profile with sts get session token credentials.".format(bastion_sts))
            sys.exit(1)

    elif "aws_session_token" not in config[bastion_sts]:
        print("An MFA token code is required when the bastion-sts does not have previous sts credentials.")
        sys.exit(1)

    #################
    # STS assume role
    #################
    try:
        bastion_sts_client = boto3.Session(profile_name=bastion_sts).client("sts")

        one_hour_in_seconds = 3600
        role_arn = config[assume_role_profile]["role_arn"]
        role_session_name = "bastion-assume-role-{}".format(random.randint(0, 1000))

        sts_assume_role_creds = bastion_sts_client.assume_role(
            DurationSeconds=one_hour_in_seconds,
            RoleArn=role_arn,
            RoleSessionName=role_session_name
        )["Credentials"]

        config[assume_role_profile]["aws_access_key_id"] = sts_assume_role_creds["AccessKeyId"]
        config[assume_role_profile]["aws_secret_access_key"] = sts_assume_role_creds["SecretAccessKey"]
        config[assume_role_profile]["aws_session_token"] = sts_assume_role_creds["SessionToken"]

        with open(aws_shared_credentials_path, 'w') as f:
            config.write(f)
        print("Setting the '{}' profile with sts assume role credentials.".format(assume_role_profile))

    except Exception:
        print("Failed to set the '{}' profile with sts assume role credentials.".format(assume_role_profile))
        sys.exit(1)


if __name__ == "__main__":
    main()
