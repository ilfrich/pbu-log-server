SHELL:=/bin/bash
include .env

start:
	python3 runner.py

clean:
	rm -f _logs/*.log*

install-deps:
	sudo pip3 install -r requirements.txt