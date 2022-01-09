# Copyright 2021 Hoshea Jiang
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

import fire

from collector.github.client import Client
from collector.github.pull_requests_collector import PullRequestsCollector
from discriminator.fasttext.discriminator import CategoryDiscriminator
from generator.markdown.generator import MarkdownGenerator
from summarizer.pg_network.summarizer import EntrySummarizer


class DeepRelease:
    """DeepRelease CLI."""

    def __init__(self, token=''):
        """Initialize DeepRelease's components.

        Args:
            token: the GitHub personal access token.
        """
        self.client = Client(token)
        self.collector = PullRequestsCollector(self.client)
        self.summarizer = EntrySummarizer()
        self.discriminator = CategoryDiscriminator()
        self.generator = MarkdownGenerator()

    def run(self, owner='', repo=''):
        """Run DeepRelease.

        Args:
            owner: the owner of the repo.
            repo: the name of the repo.

        Returns:
            None.
        """
        prs = self.collector.get_all_since_last_release(owner, repo)
        entries = self.summarizer.summarize(prs)
        categories = self.discriminator.classify(prs)
        self.generator.generate(entries, categories)


if __name__ == '__main__':
    fire.Fire(DeepRelease)
