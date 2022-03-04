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

from nltk.tokenize import sent_tokenize, word_tokenize

# patterns that need to be removed
PATTERNS = {
    'email_pattern': re.compile(
        r'(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))'),
    'url_pattern': re.compile(
        r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)'),
    'reference_pattern': re.compile(r'#[\d]+'),
    'signature_pattern': re.compile(r'(signed-off-by|co-authored-by|also-by):'),
    'at_pattern': re.compile(r'@\S+'),
}

# patterns that need to be replaced
version_pattern = r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?'
sha_pattern = r'(^|\s)[\dA-Fa-f-]{7,}(?=(\s|$))'
digit_pattern = r'(\s|-|\.)[\d]+(?=\s)'


def preprocess_title(s: str) -> [str]:
    functions = [remove_non_ascii_and_asterisk, remove_ref_and_mention, replace_words, my_strip]

    for f in functions:
        s = f(s)

    return s


def preprocess_desc_and_commits(s: str) -> [str]:
    functions = [remove_non_ascii_and_asterisk, preprocess_text, replace_words, my_strip]

    for f in functions:
        s = f(s)

    return s


def my_strip(s: str) -> [str]:
    s = str(s)
    s = s.replace('#', '')
    if s.endswith('('):
        s = s[:-1]
    s = s.strip(' \t\n\r,…')
    return word_tokenize(s)


def remove_non_ascii_and_asterisk(s: str) -> str:
    s = str(s)
    s = s.encode("ascii", "ignore").decode()
    s = s.replace('*', '')
    return s.strip().lower()


def sentence_end(text):
    pattern = r'.*[.!?]$'
    if re.match(pattern, text, re.DOTALL):
        return True
    else:
        return False


# remove sentences with url, email, mention, signature, etc.
def preprocess_text(text: str) -> str:
    temp = []
    # 根据换行来分段
    segs = text.strip().split('\n')
    for seg in segs:
        seg = seg.strip()
        if seg:
            if not sentence_end(seg):
                seg += ' .'
            temp.append(seg)

    sens = sent_tokenize(" ".join(temp))
    ret = []
    for sen in sens:
        flag = True
        for p in PATTERNS.values():
            if len(p.findall(sen)) > 0:
                flag = False
                break
        if flag:
            ret.append(sen)

    return ' '.join(ret).strip()


# replace version, sha, digit and `nan`
def replace_words(text: str) -> str:
    ret = re.sub(sha_pattern, ' sha ', text)
    ret = re.sub(version_pattern, ' version ', ret)
    ret = re.sub(digit_pattern, ' 0 ', ret)
    return ret


def remove_ref_and_mention(s: str) -> str:
    ret = PATTERNS['at_pattern'].sub('', s)
    ret = PATTERNS['reference_pattern'].sub('', ret)
    ret = PATTERNS['url_pattern'].sub('', ret)
    return re.sub(r'\((,|\s)*\)', '', ret).strip()
