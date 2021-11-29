import fire

from collector.github.client import Client
from collector.github.pull_requests_collector import PullRequestsCollector


class DeepRelease:
    """"""

    def __init__(self, token=''):
        self.token = token
        self.client = Client(token)
        self.prc = PullRequestsCollector(self.client)

    def run(self, owner='', repo=''):
        prs = self.prc.get_all_since_last_release(owner, repo)
        pass


if __name__ == '__main__':
    fire.Fire(DeepRelease)
