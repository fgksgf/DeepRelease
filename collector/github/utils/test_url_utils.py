import pytest

from collector.github.utils.url_utils import check_pull_request_url, parse_pull_request_url


@pytest.mark.parametrize("url, expected", [('https://github.com/apache/skywalking-python/pull/175', True),
                                           ('https://google.com', False)])
def test_check_pull_request_url(url, expected):
    assert check_pull_request_url(url) == expected


@pytest.mark.parametrize("url, expected", [('https://github.com/apache/skywalking-python/pull/175', ('apache', 'skywalking-python', 175))])
def test_parse_pull_request_url(url, expected):
    assert parse_pull_request_url(url) == expected
