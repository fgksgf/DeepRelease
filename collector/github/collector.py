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
from entity.pull_request import PullRequest


class PullRequestsCollector(Collector):
    def __init__(self, client: AbstractClient):
        super().__init__(client)
        self.client = client

    @logger.catch
    def get_all_during(self, owner: str, name: str, since: str = None, until: str = None) -> [PullRequest]:
        if since is None:
            logger.debug("Since is None, will use the last release date")
            commit, date = self.client.get_last_release(owner, name)
            logger.debug(f"Last release commit is {commit}, at {date}")
            since = date

        prs = []
        urls = self.client.get_pull_requests_during(owner, name, since, until)
        for url in urls:
            try:
                pr = PullRequest(url)
                pr_data = self.client.get_pull_request_info(owner, name, pr.number)
                pr.set_data(pr_data)
                prs.append(pr)
            except Exception as e:
                logger.warning(f'Failed to process the PR {url}: {e}')
                continue

        return prs
