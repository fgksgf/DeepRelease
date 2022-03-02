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

import unittest

from entity.pull_request import PullRequest
from summarizer.pg_network.summarizer import EntrySummarizer
from utils.utils import all_same

data = {
    'title': 'test',
    'bodyText': 'test',
    'commits': {'nodes': [{'commit': {'message': 'test'}}]}
}

PR_NUM = 4


def prepare_data():
    ret = []
    for i in range(PR_NUM):
        pr = PullRequest('test', 'test')
        pr.set_data(data)
        ret.append(pr)
    return ret


class TestSummarizer(unittest.TestCase):
    summarizer = EntrySummarizer()

    def test_summarize(self):
        entries = self.summarizer.summarize(prepare_data())
        self.assertEqual(len(entries), PR_NUM)
        self.assertTrue(all_same(entries))
