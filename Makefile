NO_COLOR=\033[0m
COLOR=\033[32;01m

PROJECT_NAME = pyairflow
WORKDIR = /src/py-airflow
IMAGE_NAME = dohernandez/$(PROJECT_NAME)
CONTAINER_NAME = $(PROJECT_NAME)

WEBSERVER = py-airflow-webserver

# do not edit the following lines
# for shell usage

all: usage

usage:
	@echo "build:  Build the py-airflow docker image."
	@echo "freeze:  Print all the python package installed in the py-airflow docker image."
	@echo "tests:  Run test suite using nose and print test coverage."
	@echo "airflow-run:  Run the airflow containers."
	@echo "airflow-stop:  Stop the airflow containers."
	@echo "airflow-re-build:  Stop the airflow containers and rebuild the airflow dcoker image"
	@echo "airflow-restart: Stop the airflow containers, remove them and run them again."
	@echo "airflow-freeze:  Print all the python package installed in the airflow docker image."
	@echo "airflow-log: Tail the airflow webserver container logs."
	@echo "airflow-backfill: Run backfill in airflow. Use ARG to specify airflow options. \n\t\t \
	Example: \n\t\t\t \
	make ARGS="-s 2017-07-15T02:00:00 -e 2017-07-15T02:00:00 test_external_sensor" backfill"
	@echo "airflow-list-dags: List airflow dags."

build:
	@printf "$(COLOR)==> Building $(IMAGE_NAME) docker image ...$(NO_COLOR)\n"
	@docker build -t $(IMAGE_NAME) .

freeze:
	@printf "$(COLOR)==> Checking python dependencies installed in the image ...$(NO_COLOR)\n"
	@docker run -it --rm --name $(CONTAINER_NAME) $(IMAGE_NAME) pip freeze

tests:
	@printf "$(COLOR)==> Running suite test with nose ...$(NO_COLOR)\n"
	@docker run -it --rm --name $(CONTAINER_NAME) -v $(PWD):$(WORKDIR) $(IMAGE_NAME) \
	nosetests --nocapture --nologcapture --detailed-errors --verbosity=2 --traverse-namespace \
	--with-coverage --cover-erase --cover-package=$(PROJECT_NAME) --rednose $(WORKDIR)/tests

airflow-run:
	@printf "$(COLOR)==> Spinning up containers ...$(NO_COLOR)\n"
	@docker-compose up -d

airflow-stop:
	@printf "$(COLOR)==> Stopping the containers ...$(NO_COLOR)\n"
	@docker-compose down

airflow-scheduler-run:
	@printf "$(COLOR)==> Running scheduler ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) airflow scheduler -D

airflow-re-build: stop
	@printf "$(COLOR)==> Rebuilding and spinning up containers ...$(NO_COLOR)\n"
	@docker-compose up --build -d

airflow-restart: airflow-stop airflow-run

airflow-freeze:
	@printf "$(COLOR)==> Checking python dependencies installed in the image ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) pip freeze

airflow-webserver-restart:
	@printf "$(COLOR)==> Restarting airflow ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) pkill gunicorn

airflow-webserver-log:
	@printf "$(COLOR)==> Printing service webserver log ...$(NO_COLOR)\n"
	@docker logs $(WEBSERVER)

airflow-backfill:
	@printf "$(COLOR)==> Running backfill ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) airflow backfill $(ARGS)

airflow-list-dags:
	@printf "$(COLOR)==> Listing dags ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) airflow list_dags


.PHONY: all usage build tests airflow-run airflow-stop airflow-restart airflow-re-build \
airflow-freeze airflow-webserver-restart airflow-webserver-log airflow-backfill airflow-list-dags airflow-scheduler-run
