FROM python:3.8-slim

RUN set -ex; \
	addgroup --system --gid 1002 jenkins; \
	adduser --system --uid 1002 --ingroup jenkins --home /home/jenkins jenkins; \
	apt-get --no-install-recommends update; \
	apt-get -yq --no-install-recommends upgrade; \
	apt-get install -yq --no-install-recommends git; \
	apt-get install -yq --no-install-recommends tk; \
	apt-get install -yq --no-install-recommends wget 'https://download.oracle.com/otn/java/jdk/8u371-b11/ce59cff5c23f4e2eaf4e778a117d4c5b/jdk-8u371-linux-aarch64.tar.gz'; \
	pip install --upgrade pip

WORKDIR /workspace

RUN chown -R jenkins:jenkins /workspace/

USER jenkins:jenkins
