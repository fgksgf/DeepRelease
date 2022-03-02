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
from collector.github.pull_requests_collector import PullRequestsCollector
from discriminator.fasttext.discriminator import CategoryDiscriminator
from generator.markdown.generator import MarkdownGenerator
from summarizer.pg_network.summarizer import EntrySummarizer


class DeepRelease:
    """DeepRelease CLI."""

    def __init__(self):
        """Initialize DeepRelease's components.
        """
        logger.add(sink=sys.stdout, format="{time} {level} {message}", level='INFO')
        self.initialize = False
        self.collector = None
        self.summarizer = None
        self.discriminator = None
        self.generator = None

    def initialize_components(self):
        beg = time.time()

        if self.initialize is not True:
            token = os.getenv('GITHUB_TOKEN')
            if token is None:
                logger.error('The env variable GITHUB_TOKEN is not set!')
                return

            client = Client(token)

            self.collector = PullRequestsCollector(client)
            self.summarizer = EntrySummarizer()
            self.discriminator = CategoryDiscriminator()
            self.generator = MarkdownGenerator()
            self.initialize = True

        logger.debug(f'Initialize components took {time.time() - beg} seconds.')

    @logger.catch
    def run(self, owner='', repo='', save_dir='.', save_name='release.md', debug=False, **kwargs):
        """Run DeepRelease.

        Args:
            save_name: the name of the generated file.
            save_dir: where to save the generated file.
            owner: the owner of the repo.
            repo: the name of the repo.
            debug: whether to enable debug mode.
        Returns:
            None.
        """
        if debug:
            logger.remove()
            logger.add(sink=sys.stdout, level='DEBUG')

        self.initialize_components()

        collect_beg = time.time()
        prs = self.collector.get_all_since_last_release(owner, repo)
        if len(prs) == 0:
            logger.error('No PRs to process!')
            return
        logger.info(f'{len(prs)} pull request(s) are collected in {time.time() - collect_beg} seconds.')

        summarize_beg = time.time()
        entries = self.summarizer.summarize(prs)
        logger.info(f'{len(entries)} pull request(s) are summarized in {time.time() - summarize_beg} seconds.')

        discriminate_beg = time.time()
        categories = self.discriminator.classify(prs)
        logger.info(f'{len(categories)} pull request(s) are classified in {time.time() - discriminate_beg} seconds.')

        if len(categories) != len(entries):
            logger.error('The number of change entries and change categories are not equal!')
            return

        self.generator.generate(entries, categories, save_dir=save_dir, save_name=save_name)
        logger.info(f'Done: generate the release notes: {save_dir}/{save_name}')


if __name__ == '__main__':
    fire.Fire(DeepRelease)
