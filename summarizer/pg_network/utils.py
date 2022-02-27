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

import re
import sys
import csv
import json
import time
import torch
from nltk import sent_tokenize

csv.field_size_limit(sys.maxsize)


class Params:
    def __init__(self, json_path):
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    def save(self, json_path):
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']"""
        return self.__dict__


def make_html_safe(s):
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def replace_nl(text):
    return re.sub(r'\s*<nl>\s*', r'\n', text)


def prepare_rouge_text(text):
    # replace <nl> to \n
    text = replace_nl(text)
    # pyrouge calls a perl script that puts the data into HTML files.
    # Therefore, we need to make our output HTML safe.
    text = make_html_safe(text)
    sents = sent_tokenize(text)
    text = "\n".join(sents)
    return text


def try_load_state(model_file_path):
    counter = 0
    state = None
    while True:
        if counter >= 10:
            raise FileNotFoundError
        try:
            state = torch.load(model_file_path, map_location=lambda storage, location: storage)
        except:
            time.sleep(30)
            counter += 1
            continue
        break
    return state


def sentence_end(text):
    pattern = r'.*[.!?]$'
    if re.match(pattern, text, re.DOTALL):
        return True
    else:
        return False


def ext_art_preprocess(text):
    paras = text.split(' <para-sep> ')
    cms = paras[0].split(' <cm-sep> ')
    sents = cms + paras[1:]
    new_sents = []
    for s in sents:
        s = s.strip()
        # although we already add . when preprocessing
        if s:
            if not sentence_end(s):
                s = s + ' .'
            new_sents.append(s)
    return " ".join(new_sents)


def ext_art_sent_tokenize(text):
    art = ext_art_preprocess(text)
    art_sents = sent_tokenize(art)
    return art_sents


def ext_abs_sent_tokenize(text):
    return sent_tokenize(text)
