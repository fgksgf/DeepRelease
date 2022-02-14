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

from abc import ABC, abstractmethod

from entity.category import EntryCategory
from entity.entry import Entry
from entity.group import Group


class Generator(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @abstractmethod
    def merge(self, entries: [Entry], categories: [EntryCategory], order='FBDN', **kwargs):
        """
        Merge entries that are in the same category.

        Args:
            entries: A list of change entries.
            categories: A list of change categories.
            order: The order of the categories.
            **kwargs:

        Returns:
            A list of groups.
        """
        pass

    @abstractmethod
    def generate(self, entries: [Entry], categories: [EntryCategory], **kwargs):
        """
        Generate the release note, the entry point of the generator.

        Args:
            entries: A list of change entries.
            categories: A list of change categories.
            **kwargs:

        Returns:

        """
        pass

    @abstractmethod
    def generate_content(self, groups: [Group], **kwargs):
        """
        Generate the release note's content according to the list of groups.

        Args:
            groups:
            **kwargs:

        Returns:

        """
        pass
