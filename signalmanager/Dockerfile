FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /usr/src/app
RUN apt update -y
#RUN apt install gcc python3-dev musl-dev -y
RUN apt install netcat -y
WORKDIR  /usr/src/app
COPY requirements.txt  /usr/src/app/
RUN pip install -r requirements.txt
COPY ./entrypoint.sh  /usr/src/app/entrypoint.sh
COPY . /usr/src/app/
RUN chmod 755 /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
