FROM python:3.11

RUN mkdir /app
COPY ./internals /app
COPY ./scripts/requirements.txt /app/requirements.txt
COPY ./settings /settings
WORKDIR /app
RUN pip install -r /app/requirements.txt
ARG SETTINGS_PATH=/settings
ARG SETTINGS_FILE=${SETTINGS_FILE}

ENV SETTINGS_PATH=${SETTINGS_PATH}
ENV SETTINGS_FILE=${SETTINGS_FILE}

ENTRYPOINT [ "/bin/sh"]
# sleep 2 here is to wait for database. Alternatively, there should be a script that sends periodically request to database
CMD ["-c", "sleep 2 && python main.py $SETTINGS_PATH/$SETTINGS_FILE"]
