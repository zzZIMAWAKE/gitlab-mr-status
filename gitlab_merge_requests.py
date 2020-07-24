import os
import gitlab
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


def get_request(url):
    response = requests.get(url, timeout=3)
    response.raise_for_status()
    return response.json()


gl = gitlab.Gitlab(GITLAB_HOST, PRIVATE_TOKEN)
gel_group = gl.groups.get(GITLAB_GROUP)
open_merge_requests = gel_group.mergerequests.list(
    state="opened",
    author_username=GITLAB_AUTHOR_USERNAME,
)

if not open_merge_requests:
    print("No open merge requests.")

for merge_request in open_merge_requests:
    ready_to_merge = True

    print("=" * 40)
    print(merge_request.title)

    if not merge_request.blocking_discussions_resolved:
        ready_to_merge = False
        print("*** THREADS MUST BE RESOLVED ***")

    if merge_request.has_conflicts:
        ready_to_merge = False
        print("*** CONFLICTS EXIST ***")

    if merge_request.work_in_progress:
        ready_to_merge = False
        print("*** WORK IN PROGRESS ***")

    pipelines_url = "{}/{}/merge_requests/{}/pipelines""?private_token={}".format(
        PROJECTS_URL,
        merge_request.project_id,
        merge_request.iid,
        PRIVATE_TOKEN,
    )

    pipelines = get_request(pipelines_url)

    if pipelines and pipelines[0]["status"] != "passed":
        ready_to_merge = False
        print("*** PIPELINE STATUS: {} ***".format(pipelines[0]["status"].upper()))
        print("PIPELINE URL: {}".format(pipelines[0]["web_url"]))

    if GITLAB_APPROVAL_ACCESS:
        approvals_url = "{}/{}/merge_requests/{}/approval_state""?private_token={}".format(
            PROJECTS_URL,
            merge_request.project_id,
            merge_request.iid,
            PRIVATE_TOKEN,
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

    print("URL: {}".format(merge_request.web_url))

print("=" * 40)
