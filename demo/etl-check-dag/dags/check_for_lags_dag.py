import logging

from datetime import datetime

from airflow.operators import BashOperator
from pyairflow.dag import DAG

# with DAG(
#         dag_id='check_for_lags',
#         schedule_interval='55 23 * * *',
#         start_date=datetime(2017, 07, 13, hour=23, minute=55),
# ) as dag:
#     (
#         dag
#         >> BashOperator(
#             task_id='print_date',
#             bash_command='date'
#         )
#     )

with DAG(
        dag_id='check_for_lags',
        schedule_interval='0 0 * * *',
        start_date=datetime(2017, 07, 13, hour=23, minute=55),
) as dag:
    (
        dag
        >> BashOperator(
            task_id='print_date',
            bash_command='date'
        )
    )
