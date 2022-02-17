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

from summarizer.base import Summarizer
from summarizer.pg_network import utils
from summarizer.pg_network.decode import BeamSearch


class EntrySummarizer(Summarizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def summarize(self, items):
        pass

    def preprocess(self, items):
        pass

    @staticmethod
    def decode(param_path="summarizer/pg_network/data/params.json", model_path="summarizer/pg_network/model/model",
               ngram_filter=1, data_file_prefix="test."):
        params = utils.Params(param_path)
        decode_processor = BeamSearch(params, model_path, data_file_prefix=data_file_prefix, ngram_filter=ngram_filter)
        print(decode_processor.decode())


if __name__ == "__main__":
    EntrySummarizer.decode()
