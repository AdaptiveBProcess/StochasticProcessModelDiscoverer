FROM ubuntu:20.04

# Setup python and java and base system
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8
ENV DISPLAY :99

RUN set -ex; \
	addgroup --system --gid 1002 jenkins; \
	adduser --system --uid 1002 --ingroup jenkins --home /home/jenkins jenkins; \
    apt-get --no-install-recommends update; \
	apt-get -yq --no-install-recommends upgrade; \
	apt-get install -yq --no-install-recommends git; \
	apt-get install -yq --no-install-recommends python3.8-tk; \
    apt-get install -yq openjdk-8-jdk libsnappy-dev language-pack-en supervisor; \
	apt-get install -yq --no-install-recommends software-properties-common; \	
    apt-get install -y python3-pip; \
	pip3 install --upgrade pip

WORKDIR /workspace

RUN chown -R jenkins:jenkins /workspace/

USER jenkins:jenkins
