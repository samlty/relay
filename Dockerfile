FROM ubuntu:14.04
MAINTAINER kev <abc@rchat.cn>

RUN apt-get -y install python3
ADD udproxy.py /app／
EXPOSE 1194
EXPOSE 8000
ENTRYPOINT ["/usr/bin/python3 /app/udproxy.py"]
