import glob
import os
import logging

from airflow import DAG
from airflow.models import DagBag

PROJECTS = [
    'etl-*'
]

for project in PROJECTS:
    path_projects_dag = '/usr/local/airflow/src/pyairflow/demo/{project}/dags'.format(project=project)

    for projects_dag in glob.glob(path_projects_dag):
        dhw_bag_dag = DagBag(projects_dag)

        logging.info('Filled up {dag_count} from {projects_dag}'.format(
            dag_count=dhw_bag_dag.size(),
            projects_dag=projects_dag
        ))

        if dhw_bag_dag:
            for dag_id, dag in dhw_bag_dag.dags.iteritems():
                globals()[dag_id] = dag
