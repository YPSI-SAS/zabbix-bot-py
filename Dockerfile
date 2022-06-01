FROM python:3.6-slim-buster
MAINTAINER Mélissa Bertin <melissa.bertin@ypsi.fr>
#Copy the source code in the image
WORKDIR /opt
ADD . /opt/
RUN apt-get update && \
    apt-get -y install gcc && \
    rm -rf /var/lib/apt/lists/*
#Install dependencies
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install -r requirements.txt 
WORKDIR /opt

CMD ["python", "main.py"]