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

from typing import Tuple

from collector.github.client import AbstractClient
from collector.github.collector import PullRequestsCollector


class MockClient(AbstractClient):
    def get_pull_requests_during(self, owner: str, name: str, since: str, until: str = None) -> [str]:
        return ["https://github.com/apache/skywalking-python/pull/175",
                "https://github.com/apache/skywalking-python/pull/161"]

    def get_last_release(self, owner: str, name: str) -> Tuple[str, str]:  # noqa
        return 'test', 'test'

    def get_pull_request_info(self, owner, name, num):  # noqa
        return {
            "title": "fix aiohttp outgoing request url",
            "desc": "Minor bugfix.",
            "commits":
                [
                    "fix aiohttp outgoing request url",
                    "Merge branch 'master' into master"
                ]
        }


class TestPullRequestsCollector:
    client = MockClient()
    prc = PullRequestsCollector(client)

    def test_get_all_during(self):
        prs = self.prc.get_all_during('test', 'test')
        assert len(prs) == 2
        assert prs[0].owner == 'apache' and prs[0].name == 'skywalking-python' and prs[0].number == 175
        assert prs[1].owner == 'apache' and prs[1].name == 'skywalking-python' and prs[1].number == 161
