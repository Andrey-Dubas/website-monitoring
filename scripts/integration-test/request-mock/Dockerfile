FROM python:3.11

RUN pip install flask

COPY ./request_mock.py /app/request_mock.py
WORKDIR /app

ENTRYPOINT [ "python" ]
CMD [ "request_mock.py" ]