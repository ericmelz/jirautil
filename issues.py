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
ISSUE_LIMIT = 1000


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


def is_subtask(issue):
    return issue['fields']['issuetype']['name'] == 'Sub-task'


def is_issue_finished(sprint_id, issue):
    # if issue['key'] == 'VBI-480':
    #     print('*****FOUND!')
    sprint_close_timestamp = None
    for closed_sprint in issue['fields']['closedSprints']:
        if int(sprint_id) == closed_sprint['id']:
            sprint_close_timestamp = dateutil.parser.isoparse(closed_sprint['completeDate'])
    finished = False
    finished_timestamp = None
    for entry in issue['changelog']['histories']:
        entry_timestamp = dateutil.parser.isoparse(entry['created'])
        for item in entry['items']:
            if item['field'] == 'status':
                # print(f"  {item['fromString']} -> {item['toString']}  {entry_timestamp}")
                if item['toString'] == 'Closed' and entry_timestamp < sprint_close_timestamp:
                    if finished and entry_timestamp > finished_timestamp:
                        finished_timestamp = entry_timestamp
                    elif not finished:
                        finished = True
                        finished_timestamp = entry_timestamp

    # undo finished if the item was reopened
    for entry in issue['changelog']['histories']:
        entry_timestamp = dateutil.parser.isoparse(entry['created'])
        for item in entry['items']:
            if item['field'] == 'status':
                # print(f"  {item['fromString']} -> {item['toString']}  {entry_timestamp}")
                if finished and item['fromString'] == 'Closed':
                    if entry_timestamp > finished_timestamp:
                        finished = False
    return finished


class Issue:
    def __init__(self, key, planned, finished, subtask):
        self.key = key
        self.planned = planned
        self.finished = finished
        self.subtask = subtask

    def __str__(self):
        return f'<{self.key} planned={self.planned} finished={self.finished} subtask={self.subtask}>'


def get_sprint_issues(sprint_id):
    user = os.environ.get('user')
    token = os.environ.get('token')
    url = f'{SPRINT_URL}/{sprint_id}/issue?startAt=0&maxResults={ISSUE_LIMIT}&expand=changelog'
    print(f'url={url}')
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=f'{user}:{token}')
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
    data_string = json.dumps(data, indent=4)
    # print(data_string)
    result = []
    for issue in data['issues']:
        planned = is_issue_planned(issue)
        finished = is_issue_finished(sprint_id, issue)
        subtask = is_subtask(issue)
        result.append(Issue(issue['key'], planned, finished, subtask))
    return result


def print_issues(issues):
    print('Completed:')
    for issue in [x for x in sorted(issues, key=lambda x: x.key) if x.finished and not x.subtask]:
        print(issue)
    print('\nNot Completed:')
    for issue in [x for x in sorted(issues, key=lambda x: x.key) if not x.finished and not x.subtask]:
        print(issue)


def main():
    # get_issue(ISSUE_ID)
    issues = get_sprint_issues(SPRINT_ID)
    print_issues(issues)


if __name__ == '__main__':
    main()
