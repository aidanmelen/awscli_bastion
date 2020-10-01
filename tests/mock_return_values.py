"""Mocked return values for boto3 API calls."""
from datetime import datetime

sts_get_session_token = {
    "Credentials": {
        "AccessKeyId": "string",
        "SecretAccessKey": "string",
        "SessionToken": "string",
        "Expiration": datetime(2015, 1, 1),
    }
}

sts_assume_role = {
    "Credentials": {
        "AccessKeyId": "string",
        "SecretAccessKey": "string",
        "SessionToken": "string",
        "Expiration": datetime(2015, 1, 1),
    },
    "AssumedRoleUser": {"AssumedRoleId": "string", "Arn": "string"},
    "PackedPolicySize": 123,
}

iam_get_user = {
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

iam_list_mfa_devices = {
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

iam_list_access_keys = {
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

iam_create_access_keys = {
    "AccessKey": {
        "UserName": "string",
        "AccessKeyId": "string",
        "Status": "Active",
        "SecretAccessKey": "string",
        "CreateDate": datetime(2015, 1, 1),
    }
}
