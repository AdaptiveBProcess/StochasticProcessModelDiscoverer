FROM openjdk:8-jdk

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

RUN set -ex; \
	addgroup --system --gid 1002 jenkins; \
	adduser --system --uid 1002 --ingroup jenkins --home /home/jenkins jenkins; \
    apt-get --no-install-recommends update; \
	apt-get -yq --no-install-recommends upgrade; \
	apt-get install -yq --no-install-recommends git; \
	apt-get install -yq --no-install-recommends tk; \
	apt-get install -yq --no-install-recommends software-properties-common; \
    apt-get install -y python3-pip; \
	pip install --upgrade pip

WORKDIR /workspace

RUN chown -R jenkins:jenkins /workspace/

USER jenkins:jenkins
