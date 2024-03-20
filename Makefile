PROJECTPATH := $(PWD)
INTEGRATION_TEST_SETTINGS_FILE=integration-test-settings.json

unit-test:
	docker build --no-cache -f scripts/unit-test/Dockerfile.test . -t unit-test
	docker run unit-test
	docker rmi -f unit-test

run:
	SETTINGS_FILE=${SETTINGS_FILE} docker build --no-cache -f scripts/development/Dockerfile . -t website-monitor
	docker run -e SETTINGS_FILE=${SETTINGS_FILE} -e DB_CONNECTION_STRING=${DB_CONNECTION_STRING} website-monitor
	docker rmi -f website-monitor

run-env:
	PROJECTPATH=${PROJECTPATH} SETTINGS_FILE=${SETTINGS_FILE} docker-compose -f ${PROJECTPATH}/scripts/integration-test/docker-compose.yml up

stop-env:
	docker-compose -f ${PROJECTPATH}/scripts/integration-test/docker-compose.yml down

init-local:
	python -m venv website-monitoring-venv
	. website-monitoring-venv/bin/activate
	pip install -r ./scripts/requirements.txt


run-local:
	python -m venv website-monitoring-venv && \
	. website-monitoring-venv/bin/activate && \
	pip install -r ./scripts/requirements.txt && \
	PYTHONPATH=${PYTHONPATH}:${PWD}/internals DB_CONNECTION_STRING=${DB_CONNECTION_STRING} python ./internals/main.py ${SETTINGS_FILE} && \
	deactivate