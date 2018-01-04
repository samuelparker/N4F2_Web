FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get -y install netcat
RUN apt-get -y install cron
RUN apt-get -y install vim
ADD . /code/
