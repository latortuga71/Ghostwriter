"""This contains all of functions for jira."""

# Standard Libraries
import base64
import json
import logging
import traceback
from datetime import datetime

# 3rd Party Libraries
import boto3
import pytz
import requests
import requests.auth

# Ghostwriter Libraries
from ghostwriter.commandcenter.models import JiraConfiguration

# Using __name__ resolves to ghostwriter.modules.jira
logger = logging.getLogger(__name__)

# Set timezone for dates to UTC
utc = pytz.UTC

# Digital Ocean API endpoint for droplets
jira_endpoint = "should be in the config"


class JiraTicket:
    """Compose Jira Tickets."""

    def __init__(self):
        jira_config = JiraConfiguration.get_solo()
        self.enabled = jira_config.enable
        self.api_endpoint = jira_config.api_endpoint
        self.issue_base_mode = jira_config.issue_base_mode
        self.api_key = jira_config.api_key
        self.jira_user = jira_config.jira_user
        self.default_project = jira_config.default_project

    def create_jira_project(self,project_name) -> str:
        logger.info(f"Creating project {self.api_endpoint} {self.default_project} {self.jira_user} {self.api_key}")
        auth = requests.auth.HTTPBasicAuth(self.jira_user,self.api_key)
        headers = {
            "Content-Type":"application/json",
        }
        project_data = {
            "assigneeType":"UNASSIGNED",
            "name": project_name,
            "key": project_name[0:3] + "001",
            "projectTypeKey":"software",
            "projectTemplateKey":"com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
            "leadAccountId":"63b98ecafa5fbde2ba475fe3"
        }
        endpoint = f"{self.api_endpoint}/rest/api/latest/project"
        logger.info(f"{json.dumps(project_data)} {endpoint}")
        try:
            resp = requests.post(endpoint,data=json.dumps(project_data),headers=headers,auth=auth)
            logger.info(f"response status for jira project {resp.status_code}")
            logger.info(f"text {resp.text}")
            resp_data = json.loads(resp.text)
            project_id = resp_data["key"]
            logger.info(f"project id -> {project_id}")
            return project_id
        except Exception as e:
            logger.error(f"Failed to create jira project {e}")
            return ""

    def create_issue(self,summary,description,project_key) -> str:
        logger.info(f"Creating parent isssue {self.api_endpoint} {self.default_project} {self.jira_user} {self.api_key}")
        auth = requests.auth.HTTPBasicAuth(self.jira_user,self.api_key)
        headers = {
            "Content-Type":"application/json",
        }
        issue_data = {
            "fields": {
                "project": {
                    "key": project_key
                    },
                    "summary": summary,
                    "description": description,
                    "assignee":{"name":f"{self.jira_user}"},
                    "issuetype": {
                        "name":"Task"
                    }
                }
             }
        endpoint = f"{self.api_endpoint}/rest/api/latest/issue"
        logger.info(f"{json.dumps(issue_data)} {endpoint}")
        try:
            resp = requests.post(endpoint,data=json.dumps(issue_data),headers=headers,auth=auth)
            logger.info(f"response status for jira ticket {resp.status_code}")
            logger.info(f"text {resp.text}")
            resp_data = json.loads(resp.text)
            issue_id = resp_data["key"]
            logger.info(f"issue id -> {issue_id}")
            return issue_id
        except Exception as e:
            logger.error(f"Failed to create jira parent issue {e}")
            return ""
    def create_sub_issue(self,summary,description,parent_id) -> str:
        logger.info(f"Creating sub isssue {self.api_endpoint} {self.default_project} {self.jira_user} {self.api_key}")
        auth = requests.auth.HTTPBasicAuth(self.jira_user,self.api_key)
        headers = {
            "Content-Type":"application/json",
        }
        issue_data = {
            "fields": {
                "project": {
                    "key": self.default_project
                    },
                    "summary": summary,
                    "description": description,
                    "parent":{"id":parent_id},
                    "assignee":{"name":f"{self.jira_user}"},
                    "issuetype": {
                        "name":"Sub-task"
                    }
                }
             }
        endpoint = f"{self.api_endpoint}/rest/api/latest/issue"
        logger.info(f"{json.dumps(issue_data)} {endpoint}")
        try:
            resp = requests.post(endpoint,data=json.dumps(issue_data),headers=headers,auth=auth)
            logger.info(f"response status for jira ticket {resp.status_code}")
            logger.info(f"text {resp.text}")
            resp_data = json.loads(resp.text)
            issue_id = resp_data["key"]
            logger.info(f"subissue id -> {issue_id}")
            return issue_id
        except Exception as e:
            logger.error(f"Failed to create jira parent issue {e}")
            return ""


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
