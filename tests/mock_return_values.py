"""Mocked return values for boto3 API calls."""
from datetime import datetime
from typing import Dict

sts_get_session_token: Dict = {
    "Credentials": {
        "AccessKeyId": "string",
        "SecretAccessKey": "string",
        "SessionToken": "string",
        "Expiration": datetime(2015, 1, 1),
    }
}

sts_assume_role: Dict = {
    "Credentials": {
        "AccessKeyId": "string",
        "SecretAccessKey": "string",
        "SessionToken": "string",
        "Expiration": datetime(2015, 1, 1),
    },
    "AssumedRoleUser": {"AssumedRoleId": "string", "Arn": "string"},
    "PackedPolicySize": 123,
}

iam_get_user: Dict = {
    "User": {
        "Path": "string",
        "UserName": "string",
        "UserId": "string",
        "Arn": "string",
        "CreateDate": datetime(2015, 1, 1),
        "PasswordLastUsed": datetime(2015, 1, 1),
        "PermissionsBoundary": {
            "PermissionsBoundaryType": "PermissionsBoundaryPolicy",
            "PermissionsBoundaryArn": "string",
        },
        "Tags": [{"Key": "string", "Value": "string"}],
    }
}

iam_list_mfa_devices: Dict = {
    "MFADevices": [
        {
            "UserName": "string",
            "SerialNumber": "string",
            "EnableDate": datetime(2015, 1, 1),
        },
    ],
    "IsTruncated": True,
    "Marker": "string",
}

iam_list_access_keys: Dict = {
    "AccessKeyMetadata": [
        {
            "UserName": "string",
            "AccessKeyId": "string",
            "Status": "Active",
            "CreateDate": datetime(2015, 1, 1),
        },
    ],
    "IsTruncated": True,
    "Marker": "string",
}

iam_create_access_keys: Dict = {
    "AccessKey": {
        "UserName": "string",
        "AccessKeyId": "string",
        "Status": "Active",
        "SecretAccessKey": "string",
        "CreateDate": datetime(2015, 1, 1),
    }
}
