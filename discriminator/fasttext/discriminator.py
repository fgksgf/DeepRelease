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

import fasttext
from loguru import logger

from discriminator.base import Discriminator
from discriminator.fasttext.utils import convert_str_to_category
from entity.category import EntryCategory
from entity.pull_request import PullRequest

fasttext.FastText.eprint = lambda x: None


class CategoryDiscriminator(Discriminator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = fasttext.load_model("models/fasttext.bin")

    def classify(self, items: [PullRequest]) -> [EntryCategory]:
        ret = []

        for pr in items:
            title = ' '.join(pr.title)
            try:
                c = convert_str_to_category(self.predict(title))
                ret.append(EntryCategory(pr.id, c))
            except Exception as e:
                logger.warning('Error when classifying {}: {}'.format(title, e))
                continue

        return ret

    def predict(self, title: str):
        return self.model.predict(title)[0][0][9:]
