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

import base64
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple

import requests
from loguru import logger

from collector.github.utils import has_related_pull_request, convert_to_git_timestamp
from config.constants import Constants
from github import Github


class AbstractClient(ABC):
    @abstractmethod
    def get_last_release(self, owner: str, name: str) -> Tuple[str, str]:
        pass

    @abstractmethod
    def get_pull_requests_during(self, owner: str, name: str, since: str, until: str = None) -> [str]:
        pass

    @abstractmethod
    def get_pull_request_info(self, owner: str, name: str, num: int) -> dict:
        pass


class Client(AbstractClient):
    def __init__(self, token, api_url=Constants.GITHUB_API_URL):
        self.api_url = api_url
        self.headers = {"Authorization": "token " + token}
        self.client = Github(token)

    def __query_graphql_api(self, query: str, variables: dict = None) -> dict:
        """
        Use `requests.post` to make the GitHub GraphQL API call with variables.

        Args:
            query: the GraphQL query.
            variables: variables for the query, if any.

        Returns:
            The response of the API call.
        """

        request_body = {
            'query': query,
        }
        if variables is not None:
            request_body['variables'] = variables

        response = requests.post(self.api_url,
                                 json=request_body,
                                 headers=self.headers)
        response.raise_for_status()
        data = response.json()
        if data.get('errors') is not None:
            err_msg = data.get('errors')[0].get('message')
            raise Exception(f'Bad query: {err_msg}')
        return data

    def get_pull_request_info(self, owner, name, num):
        """
        Get the information of a pull request.

        Args:
            owner: the owner of the repository.
            name: the name of the repository.
            num: the number of the pull request.

        Returns:
            A dict containing the information of the pull request, which has the following keys: title, desc and commits.
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

        ret = {}
        try:
            data = self.__query_graphql_api(query, variables)
            ret['title'] = data['data']['repository']['pullRequest']['title']
            ret['desc'] = data['data']['repository']['pullRequest']['bodyText']
            commit_msgs = []
            for node in data['data']['repository']['pullRequest']['commits']['nodes']:
                commit_msgs.append(node.get('commit').get('message'))
            ret['commits'] = commit_msgs
        except Exception as e:
            logger.error(f'Failed to get pull request info: {e}')
            return None
        return ret

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
            date = repo.get_commit(commit).commit.committer.date.strftime("%Y%m%d%H%M")
            return commit, date
        else:
            logger.warning('Can not find git tags')
            return 'None', repo.created_at.strftime("%Y%m%d%H%M")

    def get_pull_requests_during(self, owner: str, name: str, since: str, until: str = None) -> [str]:
        """
        Get all pull requests' URLs between two commits.

        Args:
            owner: the owner of the repository.
            name: the name of the repository.
            since: the beginning time or date for fetching PRs, in GitTimestamp format.
            until: the ending time or date for fetching PRs, in GitTimestamp format.

        Returns:

        """

        query = """
            query($owner : String!, $name: String!, $since: GitTimestamp!, $until: GitTimestamp!) {
              repository(name: $name, owner: $owner) {
                defaultBranchRef {
                  target {
                    ... on Commit {
                      history(since: $since, until: $until) {
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

        if until is None:
            until = datetime.now().strftime("%Y%m%d%H%M")

        variables = {
            "owner": owner,
            "name": name,
            "since": convert_to_git_timestamp(since),
            "until": convert_to_git_timestamp(until)
        }

        ret = []
        try:
            data = self.__query_graphql_api(query, variables)
            commits = data.get('data').get('repository').get('defaultBranchRef').get('target').get('history').get(
                'nodes')
            logger.debug(f'{len(commits)} commits from {since} to {until}')

            for commit in commits:
                if has_related_pull_request(commit):
                    url = commit.get('associatedPullRequests').get('nodes')[0].get('url')
                    ret.append(url)
        except Exception as e:
            logger.error(f"Error while fetching PRs' URLs from {since} to {until}: {e}")
        finally:
            return ret

    def get_template_content(self, owner: str, name: str) -> str:
        """
        Get the pull request template content from the repository, if any.

        :param owner:
        :param name:
        :return:
        """
        filenames = [
            'PULL_REQUEST_TEMPLATE.md',
            'pull_request_template.md',
            'PULL_REQUEST_TEMPLATE',
        ]

        repo = self.client.get_repo(f'{owner}/{name}')
        branch = repo.get_branch(repo.default_branch)
        for filename in filenames:
            try:
                content_encoded = repo.get_contents(f'.github/{filename}', ref=branch.commit.sha).content
                content = base64.b64decode(content_encoded).decode('utf-8')
            except Exception as e:
                logger.debug(f'Failed to get content from `.github/{filename}`: {e}')
                continue
            else:
                return content

        return ''
