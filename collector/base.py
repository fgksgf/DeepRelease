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

from abc import ABC, abstractmethod


class Collector(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def get_all_during(self, owner: str, name: str, since: str, until: str):
        """
        Get all releases data during the specified time period.

        Args:
            owner:
            name:
            since:
            until:

        Returns:

        """
        pass
