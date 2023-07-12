FROM python:3.10
LABEL authors="jadaone"

WORKDIR hr-scipt

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app ./app
COPY main.py main.py
COPY settings.py settings.py
COPY _init.py _init.py

EXPOSE 8000

ENTRYPOINT ["top", "-b"]
