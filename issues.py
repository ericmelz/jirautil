import dateutil.parser
import urllib3
import json
import os

PROJECT_ID = '15836'
# PROJECT_KEY = 'VE'
PROJECT_KEY = 'VBI'
ISSUE_URL = 'https://gumgum.jira.com/rest/api/3/issue'
SPRINT_URL = 'https://gumgum.jira.com/rest/agile/1.0/sprint'
# ISSUE_ID = '468'
ISSUE_ID = '457'
SPRINT_ID = '1010'


def get_issue(issue_id):
    user = os.environ.get('user')
    token = os.environ.get('token')
    print(f'token is {token}')
    url = f'{ISSUE_URL}/{PROJECT_KEY}-{issue_id}?expand=changelog'
    print(f'url={url}')
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=f'{user}:{token}')
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
    data_string = json.dumps(data, indent=4)
    print(data_string)


def is_issue_planned(issue):
    return False


def is_issue_finished(sprint_id, issue):
    sprint_close_timestamp = None
    for closed_sprint in issue['fields']['closedSprints']:
        if int(sprint_id) == closed_sprint['id']:
            sprint_close_timestamp = dateutil.parser.isoparse(closed_sprint['completeDate'])
    finished = False
    for entry in issue['changelog']['histories']:
        entry_timestamp = dateutil.parser.isoparse(entry['created'])
        for item in entry['items']:
            if item['field'] == 'status':
                # print(f"  {item['fromString']} -> {item['toString']}  {entry_timestamp}")
                if item['toString'] == 'Closed' and entry_timestamp < sprint_close_timestamp:
                    finished = True
    return finished


def get_sprint_issues(sprint_id):
    user = os.environ.get('user')
    token = os.environ.get('token')
    url = f'{SPRINT_URL}/{sprint_id}/issue?startAt=0&maxResults=100&expand=changelog'
    print(f'url={url}')
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=f'{user}:{token}')
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
    data_string = json.dumps(data, indent=4)
    # print(data_string)
    for issue in data['issues']:
        planned = is_issue_planned(issue)
        finished = is_issue_finished(sprint_id, issue)
        print(f"{issue['key']}   planned={planned}  finished={finished}")


def main():
    # get_issue(ISSUE_ID)
    get_sprint_issues(SPRINT_ID)


if __name__ == '__main__':
    main()
