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

VERSION ?= latest


lint:
	flake8 --version || pip install flake8
	flake8 .

ut_in_docker:
	docker run --rm --workdir /home -v $(shell pwd):/home --entrypoint="pytest" ghcr.io/fgksgf/deeprelease-base:0.1.0