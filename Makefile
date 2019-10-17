SHELL:=/bin/bash
include .env

DOCKER_REGISTRY=aur-docker-images-local.artifactory.swg-devops.com
DOCKER_IMAGE_NAME=aur-pro/log-server

start:
	python3 runner.py

clean:
	rm -f _logs/*.log*

install-deps:
	sudo pip3 install -r requirements.txt

build:
	docker build --build-arg ARTIFACTORY_PIP_URL=$(ARTIFACTORY_PIP_URL) -t $(DOCKER_IMAGE_NAME) .

push:
	docker login -u $(DOCKER_USERNAME) -p $(DOCKER_PASSWORD) $(DOCKER_REGISTRY)
	docker tag $(DOCKER_IMAGE_NAME) $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME)
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME)

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
