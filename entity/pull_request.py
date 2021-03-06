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

from entity.utils import preprocess_title, preprocess_desc_and_commits, parse_pull_request_url


class PullRequest:
    def __init__(self, url):
        self.url = url
        self.owner, self.name, self.number = parse_pull_request_url(url)

        self.title = []
        self.description = []
        self.commit_messages = []

    def set_data(self, data: dict):
        """
        Set the data of the pull request.

        :param data:
        :return:
        """
        self.title = preprocess_title(data.get('title'))
        self.description = preprocess_desc_and_commits(data.get('desc'))
        self.commit_messages = preprocess_desc_and_commits(' '.join(data.get('commits')))

    @property
    def id(self):
        return self.number

    def __str__(self):
        return str({
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'commit_messages': self.commit_messages,
        })
