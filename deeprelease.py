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
import os
import sys
import time

import fire
from loguru import logger

from collector.github.client import Client
from collector.github.collector import PullRequestsCollector
from discriminator.fasttext.discriminator import CategoryDiscriminator
from generator.markdown.generator import MarkdownGenerator
from summarizer.pg_network.summarizer import EntrySummarizer


class DeepRelease:
    """DeepRelease CLI."""

    def __init__(self):
        logger.remove()
        logger.add(sink=sys.stderr, format="<level>{level}: {message}</level>", level='INFO')

        self.initialize = False
        self.collector = None
        self.summarizer = None
        self.discriminator = None
        self.generator = None

    def initialize_components(self):
        """Initialize DeepRelease's components."""
        beg = time.time()

        if self.initialize is not True:
            token = os.getenv('GITHUB_TOKEN')
            if token is None:
                logger.error('The env variable GITHUB_TOKEN is not set!')
                exit(1)

            client = Client(token)

            self.collector = PullRequestsCollector(client)
            self.summarizer = EntrySummarizer()
            self.discriminator = CategoryDiscriminator()
            self.generator = MarkdownGenerator()
            self.initialize = True

        logger.debug(f'Initialize components took {time.time() - beg:.2f} seconds')

    @logger.catch
    def run(self, repo='', save_dir='.', save_name='release.md', debug=False, **kwargs):
        """Run DeepRelease.

        Args:
            save_name: the name of the generated file.
            save_dir: where to save the generated file.
            repo: the name of the repo.
            debug: whether to enable debug mode.

        Returns:
            None.
        """
        if debug:
            logger.remove()
            logger.add(sink=sys.stderr, level='DEBUG')

        owner, name = split_owner_repo(repo)

        self.initialize_components()

        collect_beg = time.time()
        prs = self.collector.get_all_since_last_release(owner, name)
        if prs is None or len(prs) == 0:
            logger.error('No PRs to process!')
            exit(0)
        logger.info(
            f'{len(prs)} pull request(s) are collected and preprocessed in {time.time() - collect_beg:.2f} seconds')

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


if __name__ == '__main__':
    fire.Fire(DeepRelease)
