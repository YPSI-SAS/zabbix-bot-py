FROM python:3.6-slim
MAINTAINER Mélissa Bertin <melissa.bertin@ypsi.fr>
#Copy the source code in the image
WORKDIR /opt
ADD . /opt/
#Install dependencies
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h\
    && pip install -r requirements.txt
    

WORKDIR /opt

CMD ["python", "main.py"]