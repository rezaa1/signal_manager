FROM python:3.8.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /usr/src/app
RUN apt update -y
#RUN apt install gcc python3-dev musl-dev -y
RUN apt install netcat-traditional  wget gettext vim lsb-release -y
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
#RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list
RUN apt update -y
#RUN apt-get upgrade -y
RUN apt install postgresql-client -y
WORKDIR  /usr/src/app
COPY requirements.txt  /usr/src/app/
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
COPY ./entrypoint.sh  /usr/src/app/entrypoint.sh
COPY . /usr/src/app/
#RUN find . -name migrations -type d  |  xargs rm -r

RUN chmod 755 /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
