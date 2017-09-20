FROM ubuntu:16.04

MAINTAINER cyj "chenyijiethu@gmail.com"

RUN apt-get update \
    && add-apt-repository -y ppa:fkrull/deadsnakes \
    && apt-get -y update \
    && apt-get -y install python3.5 python3-pip

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
EXPOSE 6003
CMD ["app.py"]