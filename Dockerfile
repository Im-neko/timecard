FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/app/static
WORKDIR /usr/src/app
ADD pip-requirements.txt /usr/src/app/
RUN pip install -r pip-requirements.txt
ADD . /usr/src/app/
