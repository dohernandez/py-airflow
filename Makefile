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
	@echo "build:  Build the docker image for the project."
	@echo "freeze:  Print all the python package installed in the docker image."
	@echo "tests:  Run test suite using nose and print test coverage."
	@echo "run:  Run the container."
	@echo "re-run: Stop the container, remove it and run it again."
	@echo "webserver-log: Tail the webserver container logs."

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

run:
	@printf "$(COLOR)==> Spinning up container ...$(NO_COLOR)\n"
	@docker-compose up -d

stop:
	@printf "$(COLOR)==> Stopping the container ...$(NO_COLOR)\n"
	@docker-compose down

re-run:
	@printf "$(COLOR)==> Rebuilding and spinning up container ...$(NO_COLOR)\n"
	@docker-compose up --build -d

webserver-log:
	@printf "$(COLOR)==> Printing airflow webserver log ...$(NO_COLOR)\n"
	@docker logs $(WEBSERVER)


.PHONY: all usage build tests run
