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


def re_strip(string, char=r"\W"):
    result = re.sub(f"^{char}+", "", string)
    result = re.sub(f"{char}+$", "", result)
    return result


def remove_str(s: str, t: str) -> str:
    s = str(s)
    if len(s) == 0:
        return s
    for i in t.split('\n'):
        tmp = re_strip(i).strip()
        if len(tmp) > 0:
            s = s.replace(tmp, '')
    return s
