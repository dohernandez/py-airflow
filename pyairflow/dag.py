from abc import ABCMeta
from datetime import timedelta

from airflow import DAG as AirflowDag


class DAG(AirflowDag):
    """
    A generic Dag
    """

    __metaclass__ = ABCMeta

    _owner = 'mapr'
    _depends_on_past = True
    _email = ['dwh-global@hellofresh.com']
    _email_on_failure = True
    _email_on_retry = True
    _retries = 1
    _retry_delay = timedelta(minutes=5)

    def __init__(self, dag_id, schedule_interval, start_date, **kwargs):
        super(DAG, self).__init__(
            dag_id,
            default_args={
                'owner': kwargs.get('owner', self._owner),
                'depends_on_past': kwargs.get('depends_on_past', self._depends_on_past),
                'email': kwargs.get('email', self._email),
                'email_on_failure': kwargs.get('email_on_failure', self._email_on_failure),
                'email_on_retry': kwargs.get('email_on_retry', self._email_on_retry),
                'retries': kwargs.get('retries', self._retries),
                'retry_delay': kwargs.get('retry_delay', self._retry_delay)
            },
            schedule_interval=schedule_interval,
            start_date=start_date,
            **kwargs
        )
