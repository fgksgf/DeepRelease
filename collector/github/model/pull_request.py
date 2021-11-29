from collector.github.utils.url_utils import parse_pull_request_url


class PullRequest:
    def __init__(self, url, commit):
        self.url = url
        self.commit = commit
        self.owner, self.name, self.id = parse_pull_request_url(url)

        self.title = ''
        self.description = ''
        self.commit_messages = []

    def set_data(self, data: dict):
        self.title = data.get('title')
        self.description = data.get('bodyText')
        commits = data.get('commits').get('nodes')
        for cm in commits:
            self.commit_messages.append(cm.get('commit').get('messages'))
