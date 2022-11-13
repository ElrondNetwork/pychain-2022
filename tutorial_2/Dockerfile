FROM ubuntu:20.04

RUN apt-get update && apt-get -y install python3-pip git
COPY /deep_history/ /app/deep_history/
RUN pip install -r /app/deep_history/requirements.txt --upgrade
