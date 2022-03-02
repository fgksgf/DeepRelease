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


class TestPullRequest(unittest.TestCase):
    pr = PullRequest('test', 'test')

    def test_init(self):
        self.assertEqual(self.pr.url, 'test')
        self.assertEqual(self.pr.commit, 'test')

    def test_set_data(self):
        data = {
            'title': ' test 测试 @test #55 ',
            'bodyText': ' test 测试\n @test test@test.com ### ',
            'commits': {
                'nodes': [
                    {
                        'commit': {
                            'message': '',
                        },
                    }
                ]
            }
        }
        self.pr.set_data(data)
        self.assertEqual(['test'], self.pr.title)
        self.assertEqual(['test', '.'], self.pr.description)
        self.assertEqual([], self.pr.commit_messages)
