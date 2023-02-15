init:
	pip3 install -r requirements.txt

fix:
	autopep8 --recursive --aggressive --in-place uo_manifest_patcher

set-env:
	. ./venv/bin/activate

start: set-env
	python3 uo_manifest_patcher/core.py

test: set-env
		watchmedo auto-restart \
		--patterns="*.py" \
		--directory="uo_manifest_patcher/"\
		--recursive \
		python3 uo_manifest_patcher/core.py
