FROM alpine:3

RUN apk --update --no-cache add  \
    bash  \
    git  \
    python3 \
    py3-pip \
    maven  \
    openjdk8

ADD requirements.txt /valhalla/
RUN pip3 install -r /valhalla/requirements.txt
ADD valhalla /valhalla/
ENV PYTHONPATH="${PYTHONPATH}:/valhalla"

## TESTS
#ENV CI_COMMIT_BRANCH="release-1.2.3"
#ADD valhalla.yml /

CMD ["python3", "./valhalla/main.py"]
