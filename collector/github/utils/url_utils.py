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
#
import re

PR_URL_PATTERN = re.compile(r'https://github\.com/[0-9a-z\-]+/[0-9a-z\-]+/pull/\d+')


def parse_pull_request_url(url: str):
    """
    Parse the PR url to get the repo's owner, name and the pull request number.

    :param url: The url of the pull request.
    :return: A tuple with the repo's owner, name and the pull request number.
    """
    owner, name, pr_number = '', '', ''
    url_parts = url.split("/")
    if len(url_parts) == 7:
        name = url_parts[-3]
        owner = url_parts[-4]
        pr_number = int(url_parts[-1])
    return owner, name, pr_number


def check_pull_request_url(url: str):
    """
    Check if the url is a valid pull request url.

    :param url: The url to check.
    :return: True if the url is a valid pull request url, False otherwise.
    """
    return PR_URL_PATTERN.match(url) is not None
