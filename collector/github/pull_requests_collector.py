from collector.base import Collector
from collector.github.model.pull_request import PullRequest
from collector.github.utils.url_utils import check_pull_request_url


class PullRequestsCollector(Collector):
    def __init__(self, client):
        super().__init__(client)
        self.client = client

    def get_all_since_last_release(self, owner, name):
        prs = []
        try:
            commit, date = self.client.get_last_release(owner, name)
            data = self.client.get_pull_requests_since(owner, name, date)
            if data.get('errors') is not None:
                raise Exception(data.get('errors')[0].get('message'))
            else:
                nodes = data.get('data').get('repository').get('defaultBranchRef').get('target').get('history').get('nodes')
                for node in nodes:
                    url = node.get('associatedPullRequests').get('nodes')[0].get('url')
                    commit = node.get('oid')
                    if check_pull_request_url(url):
                        pr = PullRequest(url, commit)
                        pr_data = self.client.get_pull_request_info(owner, name, pr.id)
                        if pr_data.get('errors') is not None:
                            raise Exception(pr_data.get('errors')[0].get('message'))
                        pr.set_data(pr_data.get('data').get('repository').get('pullRequest'))
                        prs.append(pr)
        except Exception as e:
            print(e)
        finally:
            return prs
