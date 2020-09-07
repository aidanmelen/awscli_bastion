"""AWSCLI Bastion STS utilities."""
import boto3


def get_user_session(session: boto3.session.Session) -> boto3.session.Session:
    """Get IAM user session.

    Args:
        session: boto3 Session.

    Returns:
        A boto3 session.
    """
    return session


def get_sts_session(session: boto3.session.Session) -> boto3.session.Session:
    """Get STS session.

    Args:
        session: boto3 Session.

    Returns:
        boto3 Session.
    """
    return session


def get_assume_role_session(session: boto3.session.Session) -> boto3.session.Session:
    """Get assume role STS session.

    Args:
        session: boto3 Session.

    Returns:
        boto3 Session.
    """
    return session
