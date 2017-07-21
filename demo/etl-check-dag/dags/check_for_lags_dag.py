from datetime import datetime

from airflow.operators.bash_operator import BashOperator
from pyairflow.dag import DAG

with DAG(
        dag_id='check_for_lags',
        schedule_interval='15 17 * * *',
        start_date=datetime(2017, 07, 14, 17, 15),
) as dag:
    (
        dag
        >> BashOperator(
            task_id='check_lag',
            bash_command='date'
        )
    )

# dag.re_scheduler('0 13 * * *')
