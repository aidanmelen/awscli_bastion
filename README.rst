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

.. image:: https://raw.githubusercontent.com/aidanmelen/awscli_bastion/master/docs/awscli-bastion.png
    :target: https://raw.githubusercontent.com/aidanmelen/awscli_bastion/master/docs/awscli-bastion.png
    :align: center


* Free software: Apache Software License 2.0
* Documentation: https://awscli-bastion.readthedocs.io.


Install
-------

::

    $ pip install awscli-bastion


Configure
---------

1. Ensure that your `AWS Bastion`_ account is `configured with mfa-protected api access`_.
2. Ensure the `awscli`_ is configured as follows:

*~/.aws/credentials*::

    # stores long-lived iam user credentials from the bastion account
    # these are fake credentials
    [bastion]
    aws_access_key_id = ASIA554SXDVIHKO5ACW2
    aws_secret_access_key = VLJQKLEqs37HCDG4HgSDrxl1vLNrk9Is8gm0VNfA

    # stores short-lived sts.get_session_token() credentials for the bastion account
    [bastion-sts]
    mfa_serial = arn:aws:iam::123456789012:mfa/aidan-melen
    credential_process = bastion get-session-token
    source_profile = bastion

    # assume role profiles store short-lived sts.assume_role() credentials
    [dev-admin]
    role_arn = arn:aws:iam::234567890123:role/admin
    source_profile = bastion-sts

    [stage-poweruser]
    role_arn = arn:aws:iam::345678901234:role/poweruser
    source_profile = bastion-sts

    [prod-spectator]
    role_arn = arn:aws:iam::456789012345:role/spectator
    source_profile = bastion-sts

*~/.aws/config*::

    [default]
    region = us-west-2
    output = json

Usage
-----

Run awscli commands normally and the configured bastion `credential_process`_ as well as the combination of `role_arn and source_profile`_ will handle the rest::

    $ aws sts get-caller-identity --profile dev-admin
    Enter MFA code for arn:aws:iam::123456789012:mfa/aidan-melen:
    {
        "UserId": "AAAAAAAAAAAAAAAAAAAAA:botocore-session-1234567890",
        "Account": "123456789012",
        "Arn": "arn:aws:sts::234567890123:assumed-role/admin/botocore-session-1234567890"
    }

    $ aws sts get-caller-identity --profile stage
    {
        "UserId": "BBBBBBBBBBBBBBBBBBBBB:botocore-session-2345678901",
        "Account": "345678901234",
        "Arn": "arn:aws:sts::345678901234:assumed-role/poweruser/botocore-session-2345678901"
    }

    $ aws sts get-caller-identity --profile prod
    {
        "UserId": "CCCCCCCCCCCCCCCCCCCCC:botocore-session-3456789012",
        "Account": "456789012345",
        "Arn": "arn:aws:sts::456789012345:assumed-role/spectator/botocore-session-3456789012"
    }

If the bastion-sts credentials cache is expired, you will be prompted for your MFA code to new sts credentials.

Force the renewal of the bastion-sts credentials cache::

    # these are fake credentials
    $ bastion get-session-token --mfa-code 123456
    {
        "AccessKeyId": "ASIA554SXXVIYYQRGGER",
        "SecretAccessKey": "aw5/hbwzGP31s2lfC3ZQshKE+AZdlOYkqBUI4otp",
        "SessionToken": "FQoGZXIvYXdHEY4aDDDbLp6g5sfNojzC6CKwAV+yefPfFg7y0xADMDECoddpj9WecBEReMtXkRjCVZfbSa1604EIK2q0zshlsP0PtF0e5wBZFDuZHTI464EpSQEXkJajksWeMMOe7PSzyJOX5Zqp8ve4ItHoE70tGxIVQjA06NbvodNjjOO/gsbDAcKHW1rx9wnq3RJ+dQbqqNq01R1vrDvTjxDNTrZr2wYI2qYrd9REP+mc44EeIO+3r0iuiwxRCL1UzS/4nG4IRYG2KMeo9esF",
        "Expiration": "2019-09-15T08:57:43+00:00",
        "Version": 1
    }

Override the default profile with attributes from an assume role profile::

    $ bastion set-default dev-admin
    Setting the 'default' profile with attributes from the 'dev-admin' profile.

    $ aws sts get-caller-identity
    {
        "UserId": "AAAAAAAAAAAAAAAAAAAAA:botocore-session-1234567890",
        "Account": "123456789012",
        "Arn": "arn:aws:sts::234567890123:assumed-role/admin/botocore-session-1234567890"
    }


Special Usage
-------------

awscli-bastion also supports `writing sts credentials to the aws shared credential file`_.

Configure *~/.aws/cli/alias* to automate the steps for each profile::

    [toplevel]

    bastion =
        !f() {
            if [ $# -eq 0 ]
            then
                bastion get-session-token --write-to-shared-credentials-file
            else
                bastion get-session-token --write-to-shared-credentials-file --mfa-code $1
            fi
            bastion assume-role dev-admin
            bastion assume-role stage-poweruser
            bastion assume-role prod-spectator
            echo "Successfully assumed roles in all AWS accounts!"
        }; f

Write sts credentials to the aws shared credentials with our ``aws bastion`` alias command::

    $ aws bastion
    Enter MFA code for arn:aws:iam::123456789012:mfa/aidan-melen:
    Setting the 'bastion-sts' profile with sts get session token credentials.
    Setting the 'dev-admin' profile with sts assume role credentials.
    Setting the 'stage-poweruser' profile with sts assume role credentials.
    Setting the 'prod-spectator' profile with sts assume role credentials.
    Successfully assumed roles in all AWS accounts!

Now your bastion-sts and assume role profiles will be populated with sts credentials.

We can clear the cached sts credentials with::

    $ bastion clear-cache
    Clearing the bastion-sts credential cache:
    - Deleted the '~/.aws/cli/cache/bastion-sts.json' file.

    Clearing sts credentials from the aws shared credentials file:
    - Skipping the 'bastion' profile because it may contain long-lived credentials.
    - STS credentials were removed from the bastion-sts profile.
    - STS credentials were removed from the dev profile.
    - STS credentials were removed from the stage profile.
    - STS credentials were removed from the prod profile.

Bastion Minimal
---------------

If you are like me, you do not trust an open-source tools and libraries to handle admin 
credentials to your aws accounts. awscli_bastion/minimal.py is written as a script that offers 
minimal bastion functionality. It is intended to be quick and easy to understand. 
A minimal number of python libraries are used to reduce security risks.

Configure 'bastion-minimal' in *~/.aws/cli/alias* to automate the steps for each profile::

    [toplevel]

    bastion-minimal =
        !f() {
            TOKEN_CODE=$1

            bastion-minimal dev-admin $TOKEN_CODE
            bastion-minimal stage-poweruser
            bastion-minimal prod-spectator

            if [ $? == 0 ]
            then
                echo "Successfully assumed roles in all AWS accounts!"
            else
                echo "Failed to assumed roles in all AWS accounts :("
            fi
        }; f

Write sts credentials to the aws shared credentials with our ``aws bastion-minimal`` alias command::

    Setting the 'bastion-sts' profile with sts get session token credentials.
    Setting the 'dev-admin' profile with sts assume role credentials.
    Setting the 'stage-poweruser' profile with sts assume role credentials.
    Setting the 'prod-spectator' profile with sts assume role credentials.
    Successfully assumed roles in all AWS accounts!

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.


.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Making a python package for pypi: http://otuk.kodeten.com/making-a-python-package-for-pypi---easy-steps
.. _`AWS Bastion`: https://blog.coinbase.com/you-need-more-than-one-aws-account-aws-bastions-and-assume-role-23946c6dfde3
.. _`configured with mfa-protected api access`: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa_configure-api-require.html
.. _`awscli`: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
.. _`credential_process`: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html
.. _`role_arn and source_profile`: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html
.. _`writing sts credentials to the aws shared credential file`: https://aws.amazon.com/premiumsupport/knowledge-center/authenticate-mfa-cli/