import re

PR_URL_PATTERN = re.compile(r'https://github\.com/[0-9a-z\-]+/[0-9a-z\-]+/pull/\d+')


def parse_pull_request_url(url: str):
    """
    Parses the pull request url to get the repo's owner, name and the pull request number.
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
    Checks if the url is a valid pull request url.
    :param url: The url to check.
    :return: True if the url is a valid pull request url, False otherwise.
    """
    return PR_URL_PATTERN.match(url) is not None
