FROM ubuntu:14.04
MAINTAINER kev <abc@rchat.cn>

RUN apt-get -y install python \
&& mkdir -p /app \
&& chmod 777 /app
ADD udproxy.py /app/
EXPOSE 1194
EXPOSE 8000
CMD ["/usr/bin/python /app/udproxy.py"]
