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
from enum import Enum


class Category(Enum):
    Features = 0
    F = 0

    BugFixes = 1
    B = 1

    Documentation = 2
    D = 2

    NonFunctional = 3
    N = 3


class EntryCategory:
    def __init__(self, entry_id: int, category: Category):
        self.entry_id = entry_id
        self.category = category
