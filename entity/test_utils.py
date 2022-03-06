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

import pytest

from entity.utils import parse_pull_request_url, preprocess_title, preprocess_desc_and_commits


class TestUtils:
    @pytest.mark.parametrize("title,expected", [
        ("test", ["test"]),
        ("测试", []),
        ("#123 test", ["test"]),
        ("@test test", ["test"]),
        ("测试test", ["test"]),
    ])
    def test_preprocess_title(self, title, expected):
        assert preprocess_title(title) == expected

    @pytest.mark.parametrize("text,expected", [
        ("test", ["test", "."]),
        ("测试", []),
        ("#123 test", []),
        ("@test test", []),
        ("测试test", ["test", "."]),
        (" test 测试\n @test test@test.com ### ", ["test", "."]),
    ])
    def test_preprocess_desc_and_commits(self, text, expected):
        assert preprocess_desc_and_commits(text) == expected

    @pytest.mark.parametrize("url, expected", [
        ('https://github.com/apache/skywalking-python/pull/175', ('apache', 'skywalking-python', 175))])
    def test_parse_pull_request_url(self, url, expected):
        assert parse_pull_request_url(url) == expected
