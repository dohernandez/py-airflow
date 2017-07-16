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
	@echo "ariflow-run:  Run the airflow containers."
	@echo "ariflow-stop:  Stop the airflow containers."
	@echo "ariflow-re-build:  Stop the airflow containers and rebuild the airflow dcoker image"
	@echo "ariflow-restart: Stop the airflow containers, remove them and run them again."
	@echo "ariflow-freeze:  Print all the python package installed in the airflow docker image."
	@echo "ariflow-log: Tail the ariflow webserver container logs."
	@echo "ariflow-backfill: Run backfill in airflow. Use ARG to specify airflow options. \n\t\t \
	Example: \n\t\t\t \
	make ARGS="-s 2017-07-15T02:00:00 -e 2017-07-15T02:00:00 test_external_sensor" backfill"
	@echo "ariflow-list-dags: List airflow dags."

build:
	@printf "$(COLOR)==> Building docker image ...$(NO_COLOR)\n"
	@docker build -t $(IMAGE_NAME) .

freeze:
	@printf "$(COLOR)==> Checking python dependencies installed in the image ...$(NO_COLOR)\n"
	@docker run -it --rm --name $(CONTAINER_NAME) $(IMAGE_NAME) pip freeze

tests:
	@printf "$(COLOR)==> Running suite test with nose ...$(NO_COLOR)\n"
	@docker run -it --rm --name $(CONTAINER_NAME) -v $(PWD):$(WORKDIR) $(IMAGE_NAME) \
	nosetests --nocapture --nologcapture --detailed-errors --verbosity=2 --traverse-namespace \
	--with-coverage --cover-erase --cover-package=$(PROJECT_NAME) --rednose $(WORKDIR)/tests

ariflow-run:
	@printf "$(COLOR)==> Spinning up containers ...$(NO_COLOR)\n"
	@docker-compose up -d

ariflow-stop:
	@printf "$(COLOR)==> Stopping the containers ...$(NO_COLOR)\n"
	@docker-compose down

ariflow-re-build: stop
	@printf "$(COLOR)==> Rebuilding and spinning up containers ...$(NO_COLOR)\n"
	@docker-compose up --build -d

restart: ariflow-stop ariflow-run

airflow-freeze:
	@printf "$(COLOR)==> Checking python dependencies installed in the image ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) pip freeze

ariflow-restart:
	@printf "$(COLOR)==> Restarting airflow ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) pkill gunicorn

ariflow-log:
	@printf "$(COLOR)==> Printing service webserver log ...$(NO_COLOR)\n"
	@docker logs $(WEBSERVER)

ariflow-backfill:
	@printf "$(COLOR)==> Running backfill ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) airflow backfill $(ARGS)

ariflow-list-dags:
	@printf "$(COLOR)==> Listing dags ...$(NO_COLOR)\n"
	@docker exec -it $(WEBSERVER) airflow list_dags


.PHONY: all usage build tests ariflow-run ariflow-stop ariflow-restart ariflow-re-build \
ariflow-freeze ariflow-restart ariflow-log ariflow-backfill ariflow-list-dags
