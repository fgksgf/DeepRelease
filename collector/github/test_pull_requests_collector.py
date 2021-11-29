from typing import Tuple

from collector.github.pull_requests_collector import PullRequestsCollector


class MockClient:
    def get_last_release(self, owner: str, name: str) -> Tuple[str, str]:
        return '', ''

    def get_pull_requests_since(self, owner: str, name: str, since: str):
        return {"data":{"repository":{"defaultBranchRef":{"target":{"history":{"nodes":[{"oid":"53066d8ccadbe3d6b3e5d534e8e2aade77fec15d","associatedPullRequests":{"nodes":[{"url":"https://github.com/apache/skywalking-python/pull/175"}]}},{"oid":"91c315b2b618c39fe534c299618efb0bf42a6e8b","associatedPullRequests":{"nodes":[{"url":"https://github.com/apache/skywalking-python/pull/161"}]}}]}}}}}}

    def get_pull_request_info(self, owner, name, num):
        return {"data":{"repository":{"pullRequest":{"commits":{"nodes":[{"commit":{"message":"fix aiohttp outgoing request url"}},{"commit":{"message":"Merge branch 'master' into master"}}]},"title":"fix aiohttp outgoing request url","bodyText":"Minor bugfix."}}}}


def test_get_all_since_last_release():
    client = MockClient()
    prc = PullRequestsCollector(client)
    prs = prc.get_all_since_last_release('test', 'test')
    assert len(prs) == 2
    assert prs[0].id == 175 and prs[1].id == 161
    assert prs[0].owner == 'apache' and prs[0].name == 'skywalking-python'
