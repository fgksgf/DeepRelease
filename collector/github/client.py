# Copyright 2022 Hoshea Jiang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import Tuple

import requests

from config.constants import Constants
from github import Github


class Client:
    def __init__(self, token='', api_url=Constants.GITHUB_API_URL):
        self.api_url = api_url
        if token == '':
            os.getenv('GHA_TOKEN', '')

        self.headers = {"Authorization": "token " + token}
        self.client = Github(token)

    def query_without_variables(self, query):
        """
        Use `requests.post` to make the API call without variables.

        :param query:
        :return:
        """
        response = requests.post(self.api_url,
                                 json={'query': query},
                                 headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

    def query_with_variables(self, query, variables):
        """
        Use `requests.post` to make the API call with variables.

        :param query:
        :param variables:
        :return:
        """
        response = requests.post(self.api_url,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))

    def get_pull_request_info(self, owner, name, num):
        """
        Get the information of a pull request.

        :param owner: the owner of the repository.
        :param name: the name of the repository.
        :param num: the number of the pull request.
        :return:
        """
        query = '''
            query($owner : String!, $name: String!, $num: Int!) {
                repository(name: $name, owner: $owner) {
                    pullRequest(number: $num) {
                        commits(first: 10) {
                            nodes {
                                commit {
                                    message
                                }
                            }
                        }
                        title
                        bodyText
                    }
                }
            }
        '''

        variables = {
            "owner": owner,
            "name": name,
            "num": num
        }

        return self.query_with_variables(query, variables)

    def get_last_release(self, owner: str, name: str) -> Tuple[str, str]:
        """
        Get the last release's commit hash and date in GitTimestamp.

        :param owner: the owner of the repository.
        :param name: the name of the repository.
        :return: (commit, date)
        """
        repo = self.client.get_repo(f'{owner}/{name}')
        tags = repo.get_tags().get_page(0)
        if len(tags) > 0:
            commit = str(tags[0].commit.sha)
            date = repo.get_commit(commit).commit.committer.date.strftime("%Y-%m-%dT%H:%M:%SZ")
            return commit, date
        else:
            raise Exception('No tags found')

    def get_pull_requests_since(self, owner: str, name: str, since: str):
        """
        Get all pull requests since a certain commit.

        :param owner: the owner of the repository.
        :param name: the name of the repository.
        :param since: the commit hash to start from, in GitTimestamp format.
        :return:
        """
        query = """
        query($owner : String!, $name: String!, $since: GitTimestamp!) {
          repository(name: $name, owner: $owner) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(since: $since) {
                    nodes {
                      oid
                      associatedPullRequests(first: 1) {
                        nodes {
                          url
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "owner": owner,
            "name": name,
            "since": since
        }
        return self.query_with_variables(query, variables)
