FROM alpine:3

RUN apk --update --no-cache add  \
    bash  \
    git  \
    python3 \
    maven  \
    openjdk8

TODO