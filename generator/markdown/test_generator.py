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

from entity.category import Category, EntryCategory
from entity.entry import Entry
from generator.markdown.generator import MarkdownGenerator


class TestMarkdownGenerator(unittest.TestCase):
    generator = MarkdownGenerator()

    entries = [
        Entry(11, "Fix bug A"),
        Entry(12, "Fix bug B"),
        Entry(13, "Fix bug C"),
        Entry(14, "Add feature A"),
        Entry(15, "Add feature B"),
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
