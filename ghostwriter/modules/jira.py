"""This contains all of functions for jira."""

# Standard Libraries
import json
import logging
import random
import traceback
from datetime import datetime

# 3rd Party Libraries
import pytz
import requests
import requests.auth

# Ghostwriter Libraries
from ghostwriter.commandcenter.models import JiraConfiguration

# Using __name__ resolves to ghostwriter.modules.jira
logger = logging.getLogger(__name__)

# Set timezone for dates to UTC
utc = pytz.UTC

class JiraTicket:
    """Compose Jira Tickets."""

    def __init__(self):
        jira_config = JiraConfiguration.get_solo()
        self.enabled = jira_config.enable
        self.api_endpoint = jira_config.api_endpoint
        self.api_key = jira_config.api_key
        self.jira_user = jira_config.jira_user
        self.jira_user_account_id = jira_config.jira_user_account_id
        self.headers = { "Content-Type":"application/json" }
        self.auth = requests.auth.HTTPBasicAuth(self.jira_user,self.api_key)

    def create_jira_project(self,project_name) -> str:
        logger.info(f"Creating jira project")
        project_data = {
            "assigneeType":"UNASSIGNED",
            "name": project_name,
            "key": f"{project_name[0:3]}{str(random.randint(100,999))}",
            "projectTypeKey":"software",
            "projectTemplateKey":"com.pyxis.greenhopper.jira:gh-simplified-kanban-classic",
            "leadAccountId":self.jira_user_account_id,
        }
        endpoint = f"{self.api_endpoint}/rest/api/latest/project"
        logger.info(f"{json.dumps(project_data)} {endpoint}")
        try:
            resp = requests.post(endpoint,data=json.dumps(project_data),headers=self.headers,auth=self.auth)
            resp_data = json.loads(resp.text)
            project_id = resp_data["key"]
            return project_id
        except Exception as e:
            logger.error(f"Failed to create jira project {e}")
            return ""

    def create_issue(self,summary,description,project_key) -> str:
        logger.info(f"creating jira issue in project {project_key}")
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
        try:
            resp = requests.post(endpoint,data=json.dumps(issue_data),headers=self.headers,auth=self.auth)
            resp_data = json.loads(resp.text)
            issue_id = resp_data["key"]
            return issue_id
        except Exception as e:
            logger.error(f"Failed to create jira issue in project {project_key} {e}")
            return ""

    def delete_issue(self,issue_id):
        logger.info(f"deleting jira issue id {issue_id}")
        endpoint = f"{self.api_endpoint}/rest/api/latest/issue/{issue_id}"
        try:
            requests.delete(endpoint,headers=self.headers,auth=self.auth)
        except Exception as e:
            logger.error(f"Failed to delete jira issue {issue_id} {e}")
            return ""

def test_jira(jira_key,jira_user,jira_endpoint):
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
