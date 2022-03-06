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

import re

PR_URL_PATTERN = re.compile(r'https://github\.com/[0-9a-z\-]+/[0-9a-zA-Z\-]+/pull/\d+')


def pull_request_url_is_valid(url: str):
    """
    Check if the url is a valid pull request url.

    :param url: The url to check.
    :return: True if the url is a valid pull request url, False otherwise.
    """
    return PR_URL_PATTERN.match(url) is not None


def has_related_pull_request(commit: dict):
    """Checks if the pull request has a related pull request."""
    return len(commit.get('associatedPullRequests').get('nodes')) > 0
