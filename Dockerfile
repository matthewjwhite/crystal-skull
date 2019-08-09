FROM oraclelinux:7

RUN yum install -y python36 && \
    curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install gevent pymongo pyyaml

ENV PYTHONUNBUFFERED=1
EXPOSE 5555

COPY config.py config.yml app.py telnet.py game.py /

CMD ["python3", "app.py"]
