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
import string

from loguru import logger

from entity.category import Category, EntryCategory
from entity.entry import Entry
from entity.group import Group
from generator.base import Generator


class MarkdownGenerator(Generator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def merge(self, entries: [Entry], categories: [EntryCategory], order='FBDN', **kwargs):
        entry_dict = {}
        for e in entries:
            entry_dict[e.id] = e

        groups = {}
        for c in categories:
            if not groups.get(c.category.value):
                groups[c.category.value] = Group(c.category)
            groups.get(c.category.value).append(entry_dict.get(c.entry_id))

        ret = []
        for o in order:
            if groups.get(Category[o].value):
                ret.append(groups[Category[o].value])
        return ret

    def generate_content(self, groups: [Group], **kwargs):
        lines = []
        for g in groups:
            lines.append(process_single_category(g.category))
            for e in g.entries:
                lines.append(process_single_entry(e))
        return '\n'.join(lines) + '\n'

    @staticmethod
    def save(content: str, save_dir: str, save_name: str):
        with open(f'{save_dir}/{save_name}', 'w') as f:
            f.write(content)

    def generate(self, entries: [Entry], categories: [Category], **kwargs):
        groups = self.merge(entries, categories, **kwargs)
        content = self.generate_content(groups, **kwargs)
        logger.debug(f'Generated markdown content:\n{content}')
        self.save(content, kwargs.get('save_dir'), kwargs.get('save_name'))


def process_single_category(c: Category) -> str:
    return f'\n## {c.name}\n'


def process_single_entry(e: Entry) -> str:
    return f"- {capitalize(e.body.rstrip('. '))} (#{e.id})"


def capitalize(s: str) -> str:
    if s:
        return s[0].upper() + s[1:]
    return s
