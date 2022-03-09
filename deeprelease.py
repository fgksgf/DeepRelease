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

"""The entrance of DeepRelease."""
import configparser
import os
import sys
import time
from datetime import datetime

import fire
from loguru import logger

from collector.github.client import Client
from collector.github.collector import PullRequestsCollector
from discriminator.fasttext.discriminator import CategoryDiscriminator
from generator.markdown.generator import MarkdownGenerator
from summarizer.pg_network.summarizer import EntrySummarizer


class DeepRelease:
    """DeepRelease CLI."""

    def __init__(self, debug=False, config=''):
        """
        Args:
            debug: whether to print debug information.

        Returns:
            None.
        """
        logger.remove()
        if debug:
            logger.add(sink=sys.stderr, level='DEBUG')
        else:
            logger.add(sink=sys.stderr, format="<level>{level}: {message}</level>", level='INFO')

        self.debug = debug
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.initialize = False
        self.collector = None
        self.summarizer = None
        self.discriminator = None
        self.generator = None

    def __initialize_components(self):
        """Initialize DeepRelease's components."""
        if self.initialize:
            return

        beg = time.time()

        if self.config.has_option('summarizer', 'model_path'):
            self.summarizer = EntrySummarizer(model_path=self.config['summarizer']['model_path'])
        else:
            self.summarizer = EntrySummarizer()

        if self.config.has_option('discriminator', 'model_path'):
            self.discriminator = CategoryDiscriminator(model_path=self.config['discriminator']['model_path'])
        else:
            self.discriminator = CategoryDiscriminator()

        self.generator = MarkdownGenerator()
        self.initialize = True
        logger.debug(f'Initialize components took {time.time() - beg:.2f} seconds')

    @logger.catch
    def collect(self, repo: str, since: str = None, until: str = None):
        """
        Collect pull requests from GitHub.

        Args:
            repo: the repository name.
            since: the beginning time or date for fetching data, in `%Y%m%d%H%M` format.
            until: the ending time or date for fetching PRs, in `%Y%m%d%H%M` format.

        Returns:
            A list of pull requests.
        """
        if self.collector is None:
            token = os.getenv('GITHUB_TOKEN')
            if token is None:
                logger.error('The env variable GITHUB_TOKEN is not set')
                exit(1)
            self.collector = PullRequestsCollector(Client(token))

        if not validate_date_format(since) or not validate_date_format(until):
            logger.error('Invalid date format, should be in %Y%m%d%H%M format')
            exit(1)

        beg = time.time()
        owner, name = split_owner_repo(repo)
        prs = self.collector.get_all_during(owner, name, since, until)
        if prs is None or len(prs) == 0:
            logger.error('No PRs to process!')
            exit(0)
        logger.info(f'{len(prs)} PR(s) are collected and preprocessed in {time.time() - beg:.2f} seconds')

        return prs

    @logger.catch
    def run(self, repo: str, save_dir='.', save_name='release.md', since: str = None, until: str = None):
        """Run DeepRelease.

        Args:
            repo: the repository name.
            save_name: the name of the generated file.
            save_dir: where to save the generated file.
            since: the beginning time or date for fetching data, in `%Y%m%d%H%M` format.
            until: the ending time or date for fetching PRs, in `%Y%m%d%H%M` format.

        Returns:
            None.
        """
        self.__initialize_components()

        prs = self.collect(repo, since, until)

        summarize_beg = time.time()
        entries = self.summarizer.summarize(prs)
        logger.info(f'{len(entries)} pull request(s) are summarized in {time.time() - summarize_beg:.2f} seconds')

        discriminate_beg = time.time()
        categories = self.discriminator.classify(prs)
        logger.info(f'{len(categories)} pull request(s) are classified in {time.time() - discriminate_beg:.2f} seconds')

        if len(categories) != len(entries):
            logger.error('The number of change entries and change categories are not equal!')
            exit(1)

        self.generator.generate(entries, categories, save_dir=save_dir, save_name=save_name)
        logger.info(f'Generate the release notes: {save_dir}/{save_name}')


def split_owner_repo(repo):
    """Split the repo name into owner and repo.

    Args:
        repo: the name of the repo.

    Returns:
        A tuple of owner and repo.
    """
    lst = repo.split('/')
    if len(lst) != 2:
        logger.error(f'The repo name {repo} is invalid, should be <owner>/<name>!')
        exit(1)
    return lst[0], lst[1]


def validate_date_format(date_str):
    """Validate the date format.

    Args:
        date_str: the date string.

    Returns:
        True if the date string is valid.
    """
    if date_str is None:
        return True

    try:
        datetime.strptime(str(date_str), '%Y%m%d%H%M')
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    fire.Fire(DeepRelease)
