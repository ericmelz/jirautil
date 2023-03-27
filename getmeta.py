import urllib3
import json
import os

PROJECT_KEY = '15836'
PROJECT_URL = 'https://gumgum.jira.com/rest/api/2/project/15836'


def main():
    user = os.environ.get('user')
    token = os.environ.get('token')
    print(f'token is {token}')
    url = 'https://gumgum.jira.com/rest/api/2/issue/createmeta'
    http = urllib3.PoolManager()
    headers = urllib3.make_headers(basic_auth=f'{user}:{token}')
    response = http.request('GET', url, headers=headers)
    data = json.loads(response.data.decode('utf-8'))
    data_string = json.dumps(data, indent=4)
    print(data_string)


if __name__ == '__main__':
    main()
