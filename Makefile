SHELL:=/bin/bash
include .env

start:
	python3 runner.py

clean:
	rm -f _logs/*.log*

install-deps:
	sudo pip3 install -r requirements.txt

check-lint:
	find . -name '*.py' | while read file; do \
	    pycodestyle $$file; \
	done; \

lint:
	find . -name '*.py' | while read file; do \
	    pycodestyle $$file; \
	    if [[ $$? != 0 ]]; then exit $$?; fi \
	done; \

local-build:
	sudo make build
