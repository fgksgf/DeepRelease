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

import csv
import time
from typing import List

from loguru import logger

from entity.entry import Entry
from entity.pull_request import PullRequest
from summarizer.base import Summarizer
from summarizer.pg_network import utils
from summarizer.pg_network.decode import BeamSearch


class EntrySummarizer(Summarizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger

    def summarize(self, items: [PullRequest]) -> [Entry]:
        data_file_name = f'input_{time.time()}.csv'
        self.logger.debug(f'Saving input to {data_file_name}')

        rows = self.save_input_to_csv(items, data_file_name)
        abstracts = self.decode(data_file_name)
        if len(items) != len(abstracts):
            self.logger.exception(f'The number of input ({len(items)}) and the number of output ({len(abstracts)}) do not match')

        entries = []
        for i in range(len(abstracts)):
            entries.append(Entry(rows[i], abstracts[i]))
        return entries

    def save_input_to_csv(self, items: [PullRequest], filename: str) -> List[List[str]]:
        rows = []

        for pr in items:
            article = self.preprocess(pr)
            rows.append([pr.id, '', article])

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'abstract', 'article'])
            writer.writerows(rows)

        return rows

    @staticmethod
    def preprocess(pr: PullRequest) -> str:
        lst = [' '.join(pr.title), ' '.join(pr.description), ' '.join(pr.commit_messages)]
        return ' [sep] '.join(lst)

    @staticmethod
    def decode(data_file, param_path="summarizer/pg_network/data/params.json", model_path="models/pg_network",
               ngram_filter=1):
        params = utils.Params(param_path)
        decode_processor = BeamSearch(params, model_path, data_file=data_file, ngram_filter=ngram_filter)
        return decode_processor.decode()


if __name__ == "__main__":
    print(EntrySummarizer.decode('test.csv'))
