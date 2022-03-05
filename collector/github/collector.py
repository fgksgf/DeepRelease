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

from loguru import logger

from collector.base import Collector
from collector.github.client import AbstractClient
from collector.github.utils import has_related_pull_request
from entity.pull_request import PullRequest
from utils.url import pull_request_url_is_valid


class PullRequestsCollector(Collector):
    def __init__(self, client: AbstractClient):
        super().__init__(client)
        self.client = client

    @logger.catch
    def get_all_since_last_release(self, owner, name) -> [PullRequest]:
        """
        Get all pull requests since last release.

        Args:
            owner: the owner of the repository.
            name: the name of the repository.

        Returns:

        """
        commit, date = self.client.get_last_release(owner, name)
        logger.debug(f"Last release commit is {commit}, at {date}")

        data = self.client.get_pull_requests_since(owner, name, date)
        if data.get('errors') is not None:
            err_msg = data.get('errors')[0].get('message')
            logger.error(f'failed to get pull requests since {date}: {err_msg}')
            return []

        commits = data.get('data').get('repository').get('defaultBranchRef').get('target').get('history').get(
            'nodes')[:-1]  # noqa: E501
        if len(commits) == 0:
            return []
        logger.debug(f'{len(commits)} commits since last release at {date}')

        prs = []

        for commit in commits:
            if not has_related_pull_request(commit):
                logger.debug(f'Commit {commit.get("oid")} has no related pull request')
                continue

            url = commit.get('associatedPullRequests').get('nodes')[0].get('url')
            try:
                if pull_request_url_is_valid(url):
                    logger.debug(f'Processing pull request: {url}')
                    pr = PullRequest(url, commit.get('oid'))
                    pr_data = self.client.get_pull_request_info(owner, name, pr.number)
                    if pr_data.get('errors') is not None:
                        logger.warning(f'Failed to get pull request #{pr.number} info: {pr_data.get("errors")[0].get("message")}')
                    pr.set_data(pr_data.get('data').get('repository').get('pullRequest'))
                    prs.append(pr)
                else:
                    logger.debug(f'Invalid pull request url: {url}')
            except Exception as e:
                logger.warning(f'Failed to process the pull request {url}: {e}')

        return prs
