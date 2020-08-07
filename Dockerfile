FROM alpine

RUN apk update && \
    apk add --no-cache python3 python3-dev make \
                       musl-dev libffi-dev py3-pip gcc
RUN pip3 install gevent pycryptodome pymongo pyyaml

ENV PYTHONUNBUFFERED=1
EXPOSE 5555

COPY game /game
COPY app.py /

CMD ["python3", "app.py"]
