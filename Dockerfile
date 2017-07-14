FROM python:2.7
MAINTAINER Darien Hernandez "dohernandez@gmail.com"

USER root

# Install packages
RUN apt-get update && apt-get install -y \
    git

# Set the working directory to /src
VOLUME ["/src/py-airflow"]
WORKDIR /src/py-airflow

# Copy the current directory contents into the container at /hellofresh/bi-etl
ADD . /src/py-airflow

# Install any needed packages for our test suite
RUN pip install --upgrade pip

RUN pip install --process-dependency-links .
RUN pip install -r test-requirements.txt