FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /usr/timecard/
WORKDIR /usr/timecard/
ADD pip-requirements.txt /usr/timecard/
RUN pip install -r pip-requirements.txt
ADD . /usr/timecard/
RUN ls
ENTRYPOINT ['gunicorn', 'server:api', '-D']
