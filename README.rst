==============
awscli_bastion
==============


.. image:: https://img.shields.io/pypi/v/awscli_bastion.svg
        :target: https://pypi.python.org/pypi/awscli_bastion

.. image:: https://img.shields.io/travis/aidanmelen/awscli_bastion.svg
        :target: https://travis-ci.org/aidanmelen/awscli_bastion

.. image:: https://readthedocs.org/projects/awscli-bastion/badge/?version=latest
        :target: https://awscli-bastion.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/aidanmelen/awscli_bastion/shield.svg
        :target: https://pyup.io/repos/github/aidanmelen/awscli_bastion/
        :alt: Updates


awscli_bastion extends the awscli by managing mfa protected short-lived credentials.

.. image:: docs/awscli-bastion.png
    :width: 200px
    :align: center
    :height: 100px


* Free software: Apache Software License 2.0
* Documentation: https://awscli-bastion.readthedocs.io.


Install
-------

::

    $ pip install awscli_bastion


Configure
---------

(required) *~/.aws/credentials*::

    # (required) aws bastion profiles

    [bastion] # these are fake credentials
    aws_access_key_id = ASIA554SXDVIHKO5ACW2
    aws_secret_access_key = VLJQKLEqs37HCDG4HgSDrxl1vLNrk9Is8gm0VNfA

    [bastion-sts]
    mfa_serial = arn:aws:iam::123456789012:mfa/aidan-melen
    credential_process = bastion get-session-token
    source_profile = bastion


    # (optional) aws assume role profiles

    [dev]
    role_arn = arn:aws:iam::234567890123:role/admin
    source_profile = bastion-sts

    [stage]
    role_arn = arn:aws:iam::345678901234:role/poweruser
    source_profile = bastion-sts

    [prod]
    role_arn = arn:aws:iam::456789012345:role/spectator
    source_profile = bastion-sts

(required) *~/.aws/config*::

    [default]
    region = us-west-2
    output = json

(opitonal) *~/.aws/cli/alias*::

    [toplevel]

    whoami = sts get-caller-identity

    bastion =
        !f() {
            bastion
        }; f

    auth =
        !f() {
            if [ $# -eq 0 ]
            then
                bastion get-session-token --write-to-shared-credentials-file
            else
                bastion get-session-token --write-to-shared-credentials-file --mfa-code $1
            fi
            bastion assume-role dev
            bastion assume-role stage
            bastion assume-role prod
            echo "Successfully assumed roles in all AWS accounts!"
        }; f


Usage
-----

Run awscli commands normally and the bastion `credential_process`_ will handle the rest::

    $ aws whoami --profile dev
    Enter MFA code for arn:aws:iam::123456789012:mfa/aidan-melen:
    {
        "UserId": "AAAAAAAAAAAAAAAAAAAAA:botocore-session-1234567890",
        "Account": "123456789012",
        "Arn": "arn:aws:sts::234567890123:assumed-role/admin/botocore-session-1234567890"
    }

    $ aws whoami --profile stage
    {
        "UserId": "BBBBBBBBBBBBBBBBBBBBB:botocore-session-2345678901",
        "Account": "345678901234",
        "Arn": "arn:aws:sts::345678901234:assumed-role/poweruser/botocore-session-2345678901"
    }

    $ aws whoami --profile prod
    {
        "UserId": "CCCCCCCCCCCCCCCCCCCCC:botocore-session-3456789012",
        "Account": "456789012345",
        "Arn": "arn:aws:sts::456789012345:assumed-role/spectator/botocore-session-3456789012"
    }

Renew the bastion-sts credentials cache::

    # these are fake credentials
    $ bastion get-session-token --mfa-code 123456
    {
        "AccessKeyId": "ASIA554SXXVIYYQRGGER",
        "SecretAccessKey": "aw5/hbwzGP31s2lfC3ZQshKE+AZdlOYkqBUI4otp",
        "SessionToken": "FQoGZXIvYXdHEY4aDDDbLp6g5sfNojzC6CKwAV+yefPfFg7y0xADMDECoddpj9WecBEReMtXkRjCVZfbSa1604EIK2q0zshlsP0PtF0e5wBZFDuZHTI464EpSQEXkJajksWeMMOe7PSzyJOX5Zqp8ve4ItHoE70tGxIVQjA06NbvodNjjOO/gsbDAcKHW1rx9wnq3RJ+dQbqqNq01R1vrDvTjxDNTrZr2wYI2qYrd9REP+mc44EeIO+3r0iuiwxRCL1UzS/4nG4IRYG2KMeo9esF",
        "Expiration": "2019-09-15T08:57:43+00:00",
        "Version": 1
    }

Replace default profile with assume_role profile::

    $ bastion set-default dev
    Setting the 'default' profile with attributes from the 'dev' profile.

    $ aws whoami
    {
        "UserId": "AAAAAAAAAAAAAAAAAAAAA:botocore-session-1234567890",
        "Account": "123456789012",
        "Arn": "arn:aws:sts::234567890123:assumed-role/admin/botocore-session-1234567890"
    }


Special Usage
-------------

Write bastion-sts credentials to the aws shared credential file::

    $ bastion get-session-token --write-to-shared-credentials-file --mfa-code 123456
    Setting the 'bastion-sts' profile with sts credential attributes.
    
    # this will set the following in the ~/.aws/credentials file
    # [bastion-sts]
    # source_profile = bastion-sts
    # aws_session_expiration = 2019-09-15T02:22:29+00:00
    # aws_access_key_id = ASIA554SXXVIYYQRGGER
    # aws_secret_access_key = aw5/hbwzGP31s2lfC3ZQshKE+AZdlOYkqBUI4otp
    # aws_session_token = FQoGZXIvYXdHEY4aDDDbLp6g5sfNojzC6CKwAV+yefPfFg7y0xADMDECoddpj9WecBEReMtXkRjCVZfbSa1604EIK2q0zshlsP0PtF0e5wBZFDuZHTI464EpSQEXkJajksWeMMOe7PSzyJOX5Zqp8ve4ItHoE70tGxIVQjA06NbvodNjjOO/gsbDAcKHW1rx9wnq3RJ+dQbqqNq01R1vrDvTjxDNTrZr2wYI2qYrd9REP+mc44EeIO+3r0iuiwxRCL1UzS/4nG4IRYG2KMeo9esF

Write assume role sts credentials to the aws shared credential file::

    $ bastion assume-role dev
    Setting the 'dev' profile with assume role sts credential attributes.

    # this will set the following in the ~/.aws/credentials file
    # [dev]
    # role_arn = arn:aws:iam::234567890123:role/admin
    # source_profile = bastion-sts
    # aws_session_expiration = 2019-09-15T02:22:29+00:00
    # aws_access_key_id = ASIA554SXXVIYYQRGGER
    # aws_secret_access_key = aw5/hbwzGP31s2lfC3ZQshKE+AZdlOYkqBUI4otp
    # aws_session_token = FQoGZXIvYXdHEY4aDDDbLp6g5sfNojzC6CKwAV+yefPfFg7y0xADMDECoddpj9WecBEReMtXkRjCVZfbSa1604EIK2q0zshlsP0PtF0e5wBZFDuZHTI464EpSQEXkJajksWeMMOe7PSzyJOX5Zqp8ve4ItHoE70tGxIVQjA06NbvodNjjOO/gsbDAcKHW1rx9wnq3RJ+dQbqqNq01R1vrDvTjxDNTrZr2wYI2qYrd9REP+mc44EeIO+3r0iuiwxRCL1UzS/4nG4IRYG2KMeo9esF

Output how much time until the bastion-sts cache credentials expire::

    $ bastion get-expiration-delta
    Checking '/Users/aidan-melen/.aws/cli/cache/bastion-sts.json' for expiration timestamp.
    The bastion-sts cached credentials will expire 11 hours from now.

If the get-session-token --write-to-shared-credentials-file is used then it will check for expiration from the aws shared credentials file::

    $ bastion get-expiration-delta
    Checking '/Users/aidan-melen/.aws/credentials' for expiration timestamp.
    The bastion-sts cached credentials will expire 11 hours from now.

Set the mfa serial number::

    $ bastion set-mfa-serial
    Setting the 'mfa_serial' attribute for the 'bastion-sts' profile.

Reset the bastion credentials cache::

    $ bastion clear-cache
    ~/.aws/cli/cache/bastion-sts.json has been removed.
    sts credentials were removed from the bastion-sts profile.
    sts credentials were removed from the dev profile.
    sts credentials were removed from the stage profile.
    sts credentials were removed from the prod profile.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Making a python package for pypi: http://otuk.kodeten.com/making-a-python-package-for-pypi---easy-steps
.. credential_process: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html
