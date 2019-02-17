#
# docker build -t simple_calculate_nginx -f common/nginx/Dockerfile .
#
FROM ubuntu:xenial

ADD ./common/sources.list /etc/apt/sources.list
RUN apt-get -y update --fix-missing && apt-get -y update

RUN apt-get install -y nginx
