FROM oraclelinux:7

RUN yum install -y python36 && \
    curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install gevent

ENV PYTHONUNBUFFERED=1
EXPOSE 5555

COPY app.py telnet.py /
