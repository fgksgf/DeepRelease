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
#
import unittest

import pytest

from entity.category import Category, EntryCategory
from entity.entry import Entry
from generator.markdown.generator import MarkdownGenerator, process_single_category, process_single_entry, capitalize


class TestMarkdownGenerator(unittest.TestCase):
    generator = MarkdownGenerator()

    entries = [
        Entry(11, "fix bug A"),
        Entry(12, "fix bug B"),
        Entry(13, "fix bug C"),
        Entry(14, "add feature A"),
        Entry(15, "add feature B"),
    ]
    entry_categories = [
        EntryCategory(11, Category.BugFix),
        EntryCategory(12, Category.BugFix),
        EntryCategory(13, Category.BugFix),
        EntryCategory(14, Category.Features),
        EntryCategory(15, Category.Features),
    ]

    def test_merge(self):
        groups = self.generator.merge(self.entries, self.entry_categories)
        self.assertEqual(2, len(groups))

        self.assertEqual(groups[0].category, Category.Features)
        self.assertEqual(2, len(groups[0].entries))
        for i in range(3, 5):
            self.assertIn(self.entries[i], groups[0].entries)

        self.assertEqual(groups[1].category, Category.BugFix)
        self.assertEqual(3, len(groups[1].entries))
        for i in range(3):
            self.assertIn(self.entries[i], groups[1].entries)

    def test_generate_content(self):
        groups = self.generator.merge(self.entries, self.entry_categories)
        content = self.generator.generate_content(groups)
        expected_content = """\n## Features\n\n- Add feature A (#14)\n- Add feature B (#15)\n\n## BugFix\n\n- Fix bug A (#11)\n- Fix bug B (#12)\n- Fix bug C (#13)\n"""
        self.assertEqual(expected_content, content)


@pytest.mark.parametrize("inputs, expected", [
    (Category.Features, '\n## Features\n'),
])
def test_process_single_category(inputs: Category, expected: str):
    assert process_single_category(inputs) == expected


@pytest.mark.parametrize("inputs, expected", [
    (Entry(1, "fix bug A"), '- Fix bug A (#1)'),
    (Entry(2, "add feature b"), '- Add feature b (#2)'),
])
def test_process_single_entry(inputs: Entry, expected: str):
    assert process_single_entry(inputs) == expected


@pytest.mark.parametrize("s, expected", [
    ("fix bug A", "Fix bug A"),
    ("add feature b", "Add feature b"),
    ("a", "A"),
    ("", ""),
    (None, None),
])
def test_capitalize(s, expected):
    assert capitalize(s) == expected
