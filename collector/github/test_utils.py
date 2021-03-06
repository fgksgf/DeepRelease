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

from collector.github.utils import pull_request_url_is_valid, has_related_pull_request, convert_to_git_timestamp


@pytest.mark.parametrize("url, expected", [('https://github.com/apache/skywalking-python/pull/175', True),
                                           ('https://google.com', False)])
def test_check_pull_request_url(url, expected):
    assert pull_request_url_is_valid(url) == expected


@pytest.mark.parametrize("commit, expected", [
    ({'associatedPullRequests': {'nodes': []}}, False),
    ({'associatedPullRequests': {'nodes': [1, 2, 3]}}, True),
])
def test_has_related_pull_request(commit: dict, expected: bool):
    assert has_related_pull_request(commit) == expected


@pytest.mark.parametrize("date, expected", [
    ('202203010230', '2022-03-01T02:30:00Z'),
    ('202203011215', '2022-03-01T12:15:00Z'),
    ('202203011359', '2022-03-01T13:59:00Z'),
])
def test_convert_to_git_timestamp(date: str, expected: str):
    assert convert_to_git_timestamp(date) == expected
