FROM python:3.7.0-stretch
RUN mkdir /code
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
