# Copyright 2021 Hoshea Jiang
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

"""The entrance of DeepRelease."""

import fire

from collector.github.client import Client
from collector.github.pull_requests_collector import PullRequestsCollector


class DeepRelease:
    """DeepRelease CLI."""

    def __init__(self, token=''):
        """
        Init DeepRelease.

        :param token: the github personal access token.
        """
        self.token = token
        self.client = Client(token)
        self.prc = PullRequestsCollector(self.client)

    def run(self, owner='', repo=''):
        """
        Run DeepRelease.

        :param owner: the owner of the repo.
        :param repo: the name of the repo.
        :return:
        """
        pass


if __name__ == '__main__':
    fire.Fire(DeepRelease)
