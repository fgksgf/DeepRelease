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

from collector.github.utils.url_utils import parse_pull_request_url
from utils.preprocess import preprocess_desc_and_commits, preprocess_title


class PullRequest:
    def __init__(self, url, commit):
        self.url = url
        self.commit = commit
        self.owner, self.name, self.pr_num = parse_pull_request_url(url)

        self.title = []
        self.description = []
        self.commit_messages = []

        self.__id = hash(self.url)

    def set_data(self, data: dict):
        """
        Set the data of the pull request.

        :param data:
        :return:
        """
        self.title = preprocess_title(data.get('title'))
        self.description = preprocess_desc_and_commits(data.get('bodyText'))
        commits = data.get('commits').get('nodes')
        temp = []
        for cm in commits:
            temp.append(cm.get('commit').get('messages'))
        self.commit_messages = preprocess_desc_and_commits(' '.join(temp))

    @property
    def id(self):
        return self.__id
