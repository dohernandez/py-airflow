import logging

from datetime import datetime
from airflow.operators import BashOperator
from pyairflow.dag import DAG
from pyairflow.dag_task import ExternalTaskSensorDAGTask

with DAG(
        dag_id='test_external_sensor',
        schedule_interval='20 17 * * *',
        start_date=datetime(2017, 07, 15, hour=17, minute=20)
) as dag:
    (
        dag
        >> ExternalTaskSensorDAGTask(
            task_id='check_for_lags_sensor',
            external_dag_id='check_for_lags',
            external_task_id='print_date'
        )
        >> BashOperator(
            task_id='print_test',
            bash_command='echo test'
        )
    )
