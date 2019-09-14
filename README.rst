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


* Free software: Apache Software License 2.0
* Documentation: https://awscli-bastion.readthedocs.io.


Install
-------

::

    $ pip install awscli_bastion


Configure
---------

*~/.aws/credentials*::

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

*~/.aws/config*::

    [default]
    region = us-west-2
    output = json


Usage
-----

Run awscli commands normally and the bastion credential_process will handle the rest.::

    $ aws sts get-caller-identity --profile dev
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

Renew the bastion credentials cache.::

    $ bastion get-session-token --mfa-code 123456

Replace default profile with assume_role profile.::

    $ bastion set-default dev
    updating the default profile with the dev profile

Reset the bastion credentials cache.::

    $ bastion resert-cache

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Making a python package for pypi: http://otuk.kodeten.com/making-a-python-package-for-pypi---easy-steps
