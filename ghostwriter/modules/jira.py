"""This contains all of functions for checking jira connectivity."""

# Using __name__ resolves to ghostwriter.modules.cloud_monitors
logger = logging.getLogger(__name__)  # Standard Libraries
# Standard Libraries
import logging
import traceback
from datetime import datetime

# 3rd Party Libraries
import boto3
import pytz
import requests

# Set timezone for dates to UTC
utc = pytz.UTC

# Digital Ocean API endpoint for droplets
jira_endpoint = "https://api.digitalocean.com/v2/droplets"


def test_jira(jira_key):
    """
    Test JIRA keys by connecting to jira`.

    **Parameters**

    ``jira_key``
        AWS key with access to the service
    """
    messages = []
    try:
        # TODO DO JIRA API REQUEST
        return {"capable": True, "message": messages}
    except requests.RequestException:
        logger.error(
            "AWS could not validate the provided credentials with STS; check your AWS policies"
        )
        messages.append(
            "AWS could not validate the provided credentials for EC2; check your attached AWS policies"
        )
    except Exception:
        logger.exception("Testing authentication to Jira failed")
        messages.append(
            f"Testing authentication to Jira failed: {traceback.format_exc()}"
        )
    return {"capable": False, "message": messages}
