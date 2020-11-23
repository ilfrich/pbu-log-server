SHELL:=/bin/bash
include .env

start:
	python runner.py

clean:
	rm -f _logs/*.log*

install-deps:
	sudo pip install -r requirements.txt

check-lint:
	find . -name '*.py' | while read file; do \
	    pycodestyle $$file; \
	done; \

lint:
	find . -name '*.py' | while read file; do \
	    pycodestyle $$file; \
	    if [[ $$? != 0 ]]; then exit $$?; fi \
	done; \

docker-build:
	docker build -t ilfrich/pbu-log-server .
