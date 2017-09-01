FROM ubuntu:14.04
MAINTAINER kev <abc@rchat.cn>

RUN apt-get -y install python3 \
&& mkdir -p /app
ADD udproxy.py /app/
EXPOSE 1194
EXPOSE 8000
CMD ["python3 /app/udproxy.py"]
