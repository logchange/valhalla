FROM alpine:3

# Labels.
LABEL org.opencontainers.image.authors='peter.zmilczak@gmail.com' \
      org.opencontainers.image.url='https://github.com/logchange/valhalla' \
      org.opencontainers.image.documentation='https://github.com/logchange/valhalla/blob/master/README.md' \
      org.opencontainers.image.source='https://github.com/logchange/valhalla' \
      org.opencontainers.image.vendor='The LogChange Community' \
      org.opencontainers.image.licenses='Apache-2.0'

RUN apk --update --no-cache add  \
    bash  \
    git  \
    git-lfs \
    python3 \
    py3-pip \
    maven  \
    openjdk8

ENV VALHALLA_SRC="/opt/valhalla/"
ADD requirements.txt $VALHALLA_SRC
RUN pip3 install --break-system-packages --user -r ${VALHALLA_SRC}requirements.txt
ADD valhalla $VALHALLA_SRC/valhalla
ADD __main__.py $VALHALLA_SRC
ENV PYTHONPATH="${PYTHONPATH}:${VALHALLA_SRC}"

ARG WORKING_REPO_PATH="/repository"
RUN mkdir $WORKING_REPO_PATH
WORKDIR $WORKING_REPO_PATH


CMD ["python3", "-u", "/opt/valhalla"]
