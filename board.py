import urllib3
import json
import os


BOARD_ID = '338'
BOARD_URL = 'https://gumgum.jira.com/rest/agile/1.0/board'


class Board:
    sprints = []


class Sprint:
    issues = []


class Issue:
    def __init__(self, key):
        self.key = key


def get_sprints():
    user = os.environ.get('user')
    token = os.environ.get('token')
    print(f'token is {token}')
    url = f'{BOARD_URL}/{BOARD_ID}/sprint'
    print(f'url={url}')
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=f'{user}:{token}')
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
    data_string = json.dumps(data, indent=4)
    print(data_string)


def test1():
    board = Board()
    i1 = Issue('VE-123')
    s1 = Sprint()
    s1.issues.append(i1)
    board.sprints.append(s1)
    print(board)


def main():
    get_sprints()


if __name__ == '__main__':
    main()
