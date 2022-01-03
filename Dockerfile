FROM python:3.9.7-buster

WORKDIR /src
COPY ./src /src

RUN pip install --no-cache -r /src/requirements.txt

ENTRYPOINT ["/bin/sh", "-l", "-c"]

CMD ["uvicorn main:app --reload --host 0.0.0.0 --port 80"]