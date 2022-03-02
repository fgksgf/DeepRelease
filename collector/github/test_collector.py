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
from collector.github.pull_requests_collector import PullRequestsCollector


class MockClient(AbstractClient):
    def get_last_release(self, owner: str, name: str) -> Tuple[str, str]:  # noqa
        return '', ''

    def get_pull_requests_since(self, owner: str, name: str, since: str):  # noqa
        return {"data":{"repository":{"defaultBranchRef":{"target":{"history":{"nodes":[{"oid":"53066d8ccadbe3d6b3e5d534e8e2aade77fec15d","associatedPullRequests":{"nodes":[{"url":"https://github.com/apache/skywalking-python/pull/175"}]}},{"oid":"91c315b2b618c39fe534c299618efb0bf42a6e8b","associatedPullRequests":{"nodes":[{"url":"https://github.com/apache/skywalking-python/pull/161"}]}}]}}}}}} # noqa

    def get_pull_request_info(self, owner, name, num):  # noqa
        return {"data":{"repository":{"pullRequest":{"commits":{"nodes":[{"commit":{"message":"fix aiohttp outgoing request url"}},{"commit":{"message":"Merge branch 'master' into master"}}]},"title":"fix aiohttp outgoing request url","bodyText":"Minor bugfix."}}}} # noqa


def test_get_all_since_last_release():  # noqa
    client = MockClient()
    prc = PullRequestsCollector(client)
    prs = prc.get_all_since_last_release('test', 'test')
    assert len(prs) == 1
    assert prs[0].owner == 'apache' and prs[0].name == 'skywalking-python'
