### Setup

* You'll need to install python-gitlab with `sudo pip install python-gitlab` or `sudo pip install -r requirements.txt`

* The following environment variables will need to be set up, I advise adding them to your bash profile:
    * `GITLAB_AUTHOR_USERNAME` - your username on gitlab
    * `GITLAB_ACCESS_TOKEN` - your private gitlab access token - https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
    * `GITLAB_GROUP` - the group your repositories are in e.g. `google`
    * `GITLAB_APPROVAL_ACCESS` - `1` if you have gitlab Starter / Bronze tier+, `0` otherwise (without access to this endpoint approval status will not show)

* Some optional extras that you can add to your bash profile:
    * `alias listmerge="python3 <path>/gitlab_merge_requests.py"` - allows you to type `listmerge` to run the script
    * `listmerge` - runs the above alias as soon as a terminal session is started

### Usage

Run directly: `python gitlab_merge_requests.py`

If you added the above alias: `listmerge`