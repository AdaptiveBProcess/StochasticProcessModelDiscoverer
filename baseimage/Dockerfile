FROM python:3.8-slim

RUN set -ex; \
	addgroup --system --gid 1002 jenkins; \
	adduser --system --uid 1002 --ingroup jenkins --home /home/jenkins jenkins; \
	apt-get update; \
	apt-get install -yq --no-install-recommends software-properties-common; \
	add-apt-repository -y ppa:openjdk-r/ppa; \
	apt-get update; \
	apt-get -yq --no-install-recommends upgrade; \
	apt-get install -yq --no-install-recommends git; \
	apt-get install -yq --no-install-recommends tk; \
	apt-get install -y openjdk-8-jdk; \
	pip install --upgrade pip

WORKDIR /workspace

RUN chown -R jenkins:jenkins /workspace/

USER jenkins:jenkins
