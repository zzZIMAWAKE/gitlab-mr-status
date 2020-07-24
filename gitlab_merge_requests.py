import os
import requests

GITLAB_GROUP = os.getenv("GITLAB_GROUP")
PRIVATE_TOKEN = os.getenv("GITLAB_ACCESS_TOKEN")
GITLAB_AUTHOR_USERNAME = os.getenv("GITLAB_AUTHOR_USERNAME")

# Approvals endpoint requires GitLab Starter / Bronze+
# You should set this env var is 0 if you do not have access, 1 otherwise
# https://docs.gitlab.com/ee/api/merge_request_approvals.html#get-the-approval-state-of-merge-requests
GITLAB_APPROVAL_ACCESS = bool(int(os.getenv("GITLAB_APPROVAL_ACCESS")))

GITLAB_HOST = "https://www.gitlab.com"
PROJECTS_URL = "{}/api/v4/projects".format(GITLAB_HOST)
MR_URL = "{host}/api/v4/groups/{group}/merge_requests?private_token={token}&state={state}&author_username={author}"
PIPELINES_URL = "{projects_url}/{project_id}/merge_requests/{mr_iid}/pipelines""?private_token={token}"
APPROVALS_URL = "{projects_url}/{project_id}/merge_requests/{mr_iid}/approval_state""?private_token={token}"


def get_request(url):
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()


merge_requests_url = MR_URL.format(
    host=GITLAB_HOST,
    group=GITLAB_GROUP,
    token=PRIVATE_TOKEN,
    state="opened",
    author=GITLAB_AUTHOR_USERNAME,
)
open_merge_requests = get_request(merge_requests_url)

if not open_merge_requests:
    print("No open merge requests.")

for merge_request in open_merge_requests:
    ready_to_merge = True

    print("=" * 40)
    print(merge_request["title"])

    if not merge_request["blocking_discussions_resolved"]:
        ready_to_merge = False
        print("*** THREADS MUST BE RESOLVED ***")

    if merge_request["has_conflicts"]:
        ready_to_merge = False
        print("*** CONFLICTS EXIST ***")

    if merge_request["work_in_progress"]:
        ready_to_merge = False
        print("*** WORK IN PROGRESS ***")

    pipelines_url = PIPELINES_URL.format(
        projects_url=PROJECTS_URL,
        project_id=merge_request["project_id"],
        mr_iid=merge_request["iid"],
        token=PRIVATE_TOKEN,
    )

    pipelines = get_request(pipelines_url)

    if pipelines and pipelines[0]["status"] != "success":
        ready_to_merge = False
        print("*** PIPELINE STATUS: {} ***".format(pipelines[0]["status"].upper()))
        print("PIPELINE URL: {}".format(pipelines[0]["web_url"]))

    if GITLAB_APPROVAL_ACCESS:
        approvals_url = APPROVALS_URL.format(
            projects_url=PROJECTS_URL,
            project_id=merge_request["project_id"],
            mr_iid=merge_request["iid"],
            token=PRIVATE_TOKEN,
        )

        approvals = get_request(approvals_url)

        required_approvals = approvals["rules"][0]["approvals_required"]
        required_approvals = required_approvals if required_approvals > 0 else 1
        current_approvals = len(approvals["rules"][0]["approved_by"])

        if current_approvals < required_approvals:
            ready_to_merge = False
            print("*** REQUIRES APPROVAL ***")

    if ready_to_merge:
        print("*** READY TO MERGE ***")

    print("URL: {}".format(merge_request["web_url"]))

print("=" * 40)
