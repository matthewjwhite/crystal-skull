FROM oraclelinux:7

RUN yum install -y python36 && \
    curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install gevent pycryptodome pymongo pyyaml

ENV PYTHONUNBUFFERED=1
EXPOSE 5555

COPY game /game
COPY app.py /

CMD ["python3", "app.py"]
