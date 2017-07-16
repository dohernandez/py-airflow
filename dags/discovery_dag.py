import glob
import os
import logging

from airflow import DAG
from airflow.models import DagBag

PROJECTS = [
    'etl-check-dag',
    'etl-sensor-dag'
]

for project in PROJECTS:
    dir_project_dag = '/usr/local/airflow/src/pyairflow/{project}'.format(project=project)

    dhw_bag_dag = DagBag(dir_project_dag)

    logging.info('Filled up {dag_count} from {dir_project_dag}'.format(
        dag_count=dhw_bag_dag.size(),
        dir_project_dag=dir_project_dag
    ))

    if dhw_bag_dag:
        for dag_id, dag in dhw_bag_dag.dags.iteritems():
            globals()[dag_id] = dag
