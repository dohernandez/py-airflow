import logging

from datetime import datetime
from airflow.operators import BashOperator
from pyairflow.dag import DAG
from pyairflow.dag_task import ExternalTaskSensorDAGTask

with DAG(
        dag_id='test_external_sensor',
        schedule_interval='00 2 * * *',
        start_date=datetime(2017, 07, 14, hour=2, minute=00)
) as dag_1:
    (
        dag_1
        >> ExternalTaskSensorDAGTask(
            task_id='check_for_lags_sensor',
            external_dag_id='check_for_lags',
            external_task_id='print_date'
        )
        >> BashOperator(
            task_id='print_date_2',
            bash_command='date'
        )
    )