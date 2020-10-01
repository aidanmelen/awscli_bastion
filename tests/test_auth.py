"""Test cases for the auth module."""
from unittest.mock import call
from unittest.mock import Mock

from . import mock_return_values
from awscli_bastion import auth
from awscli_bastion import cache
from awscli_bastion import credentials


def test_get_session_token_wrapper_uses_api(boto3_api_call: Mock) -> None:
    """It calls the GetSessionToken api."""
    session = auth.STS(
        bastion="bastion",
        bastion_sts="bastion-sts",
        region="us-west-2",
        credentials=credentials.Credentials(),
        cache=cache.Cache(),
    ).get_session_token(mfa_code="123456")

    boto3_api_call.assert_has_calls(
        [
            call(
                "GetSessionToken",
                {
                    "DurationSeconds": 43200,
                    "SerialNumber": "arn:aws:iam::123456789012:mfa/aidan-melen",
                    "TokenCode": "123456",
                },
            )
        ],
        any_order=False,
    )
    assert (
        session["AccessKeyId"]
        == mock_return_values.sts_get_session_token["Credentials"]["AccessKeyId"]
    )


# def test_assume_role_wrapper_uses_api(boto3_api_call: Mock) -> None:
#     """It calls the AssumeRole api."""
#     session = auth.STS(
#         bastion="bastion",
#         bastion_sts="bastion-sts",
#         region="us-west-2",
#         credentials=credentials.Credentials(),
#         cache=cache.Cache(),
#     ).assume_role("dev-admin")

#     boto3_api_call.assert_has_calls(
#         [call("AssumeRole", "blarg")], any_order=False,
#     )
#     assert (
#         session.get_credentials().access_key
#         == mock_return_values.sts_assume_role["Credentials"]["AccessKeyId"]
#     )
