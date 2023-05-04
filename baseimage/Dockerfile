FROM python:3.8-slim

RUN set -ex; \
    addgroup --system --gid 1002 jenkins; \
    adduser --system --uid 1002 --ingroup jenkins --home /home/jenkins jenkins; \
    apt-get --no-install-recommends update; \
    apt-get -yq --no-install-recommends upgrade; \
    apt-get install -yq --no-install-recommends wget default-jre; \
    pip install --upgrade pip

WORKDIR /workspace

RUN chown -R jenkins:jenkins /workspace/

USER jenkins:jenkins
