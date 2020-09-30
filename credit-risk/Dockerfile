FROM FROM alpine:3.7

LABEL maintainer="hien@nguyen"

WORKDIR /tmp/

RUN apk update \
    && apk upgrade \
    && apk add git make g++ boost-dev zlib-dev python3-dev redis

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r ./requirements.txt
RUN rm -rf /var/cache/apk/*

COPY app.py basic_auth.py ./
COPY routes/ ./routes

EXPOSE 5002

CMD python3 app.py
