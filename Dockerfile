FROM ubuntu:latest
LABEL authors="irane"

ENTRYPOINT ["top", "-b"]