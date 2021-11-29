VERSION ?= latest

install:
	pip install -r requirements.txt

lint:
	pip install -r requirements-style.txt
	flake8 .

ut: install
	pytest
