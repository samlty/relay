FROM python:2.7.13-wheezy
MAINTAINER kev <abc@rchat.cn>


ADD udproxy.py /opt/
ADD proxy.conf /opt/
CMD /usr/bin/python /opt/udproxy.py
