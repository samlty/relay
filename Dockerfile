FROM alpine
MAINTAINER kev <noreply@easypi.pro>

RUN set -xe \
    && apk add --no-cache curl python3 \
    && curl -sSL https://bootstrap.pypa.io/get-pip.py | python3
ADD udproxy.py /app
EXPOSE 1194
EXPOSE 8000
CMD ["python3 /app/udproxy.py"]
