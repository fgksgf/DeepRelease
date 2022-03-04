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

from utils.url import check_pull_request_url, parse_pull_request_url


@pytest.mark.parametrize("url, expected", [('https://github.com/apache/skywalking-python/pull/175', True),
                                           ('https://google.com', False)])
def test_check_pull_request_url(url, expected):
    assert check_pull_request_url(url) == expected


@pytest.mark.parametrize("url, expected", [
    ('https://github.com/apache/skywalking-python/pull/175', ('apache', 'skywalking-python', 175))])
def test_parse_pull_request_url(url, expected):
    assert parse_pull_request_url(url) == expected
