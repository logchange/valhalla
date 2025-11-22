FROM alpine:3

# Labels.
LABEL org.opencontainers.image.title="valhalla" \
      org.opencontainers.image.authors='team@logchange.dev' \
      org.opencontainers.image.vendor='The logchange Community' \
      org.opencontainers.image.url='https://github.com/logchange/valhalla' \
      org.opencontainers.image.documentation='https://logchange.dev/tools/valhalla/' \
      org.opencontainers.image.source='https://github.com/logchange/valhalla' \
      org.opencontainers.image.licenses='Apache-2.0'

# py3-yaml - Alpine uses musl, not glibc
#   Most PyPI wheels for PyYAML do not include musl-compatible binaries
#   Therefore pip tries to build PyYAML from source, but you have no compiler or dependencies installed
RUN apk --update --no-cache add  \
    bash  \
    git  \
    git-lfs \
    zip \
    unzip \
    python3 \
    py3-pip \
    py3-yaml \
    maven  \
    openjdk8 \
    nodejs \
    npm && \
    npm install -g pnpm

RUN wget https://github.com/logchange/logchange/releases/download/1.19.12/logchange-linuxx64.zip \
    && unzip logchange-linuxx64.zip \
    && mv bins/logchange-linuxx64/logchange /usr/local/bin/logchange \
    && chmod +x /usr/local/bin/logchange \
    && rm -rf logchange-linuxx64.zip bins

ENV VALHALLA_SRC="/opt/valhalla"
ADD requirements.txt ${VALHALLA_SRC}/
RUN pip3 install --break-system-packages --root-user-action ignore -r ${VALHALLA_SRC}/requirements.txt
ADD valhalla ${VALHALLA_SRC}/valhalla
ADD __main__.py ${VALHALLA_SRC}/
ENV PYTHONPATH="${VALHALLA_SRC}"

ADD requireoments_verify.py /opt/
RUN python3 /opt/requireoments_verify.py

ARG WORKING_REPO_PATH="/repository"
RUN mkdir $WORKING_REPO_PATH
WORKDIR $WORKING_REPO_PATH

# Create "valhalla" command that calls python3 -u /opt/valhalla
RUN printf '#!/bin/sh\nexec python3 -u /opt/valhalla "$@"\n' \
    > /usr/local/bin/valhalla \
    && chmod +x /usr/local/bin/valhalla

RUN ls -l /usr/local/bin/

# we used to use CMD ["python3", "-u", "/opt/valhalla"] but valhalla is simpler :)
CMD ["valhalla"]
