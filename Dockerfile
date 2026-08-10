FROM ubuntu:latest
LABEL authors="wanho"

ENTRYPOINT ["top", "-b"]