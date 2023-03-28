SHELL := /bin/bash

install:
	pip install -r requirements.txt

fix:
	autopep8 --recursive --aggressive --in-place uopatcher

set-env:
	[[ -f ./venv/bin/activate ]] && . ./venv/bin/activate

start: set-env
	python3 uopatcher/core.py

test: set-env
		watchmedo auto-restart \
		--patterns="*.py" \
		--directory="uopatcher/"\
		--recursive \
		python3 uopatcher/core.py
