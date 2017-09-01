FROM python:2.7.13-wheezy
MAINTAINER kev <abc@rchat.cn>


mkdir -m 775 -p /app 
ADD udproxy.py /app
EXPOSE 1194
EXPOSE 8000
CMD ["/usr/bin/python /app/udproxy.py"]
