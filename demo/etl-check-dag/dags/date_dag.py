import logging

from datetime import datetime

from airflow.operators import BashOperator
from pyairflow.dag import DAG

with DAG(
        dag_id='print_date',
        schedule_interval='40 17 * * *',
        start_date=datetime(2017, 07, 16, 17, 40),
) as dag:
    (
        dag
        >> BashOperator(
            task_id='print_date',
            bash_command='date'
        )
    )

# dag.re_scheduler('0 13 * * *')
