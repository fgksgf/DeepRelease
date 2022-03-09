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

from deeprelease import split_owner_repo, validate_date_format


@pytest.mark.parametrize("test_input,expected", [
    ("foo/bar", ("foo", "bar")),
    ("owner/name", ("owner", "name")),
])
def test_split_owner_repo(test_input, expected):
    assert split_owner_repo(test_input) == expected


@pytest.mark.parametrize("date,expected", [
    ("", False),
    ("test", False),
    (None, True),
    ("202210142230", True),
    ("2022101422301", False),
    ("20221014", False),
])
def test_validate_date_format(date, expected):
    assert validate_date_format(date) == expected
