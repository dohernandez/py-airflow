import inspect
from abc import ABCMeta

from datetime import timedelta, datetime

from airflow import DAG as AirflowDag, models
from airflow import settings
from airflow.utils.dates import cron_presets
from airflow.utils.state import State


class DAG(AirflowDag):
    """
    A generic Dag
    """

    __metaclass__ = ABCMeta

    _owner = 'mapr'
    _depends_on_past = True
    _email = ['dohernandez@gmail.com']
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

        self.fileloc = inspect.stack()[1][1]

    def re_scheduler(self, re_schedule_interval):
        self.set_schedule_interval(re_schedule_interval)
        self.update_last_run()

    def set_schedule_interval(self, re_schedule_interval):
        self.schedule_interval = re_schedule_interval
        if re_schedule_interval in cron_presets:
            self._schedule_interval = cron_presets.get(re_schedule_interval)
        elif re_schedule_interval == '@once':
            self._schedule_interval = None
        else:
            self._schedule_interval = re_schedule_interval

    def update_last_run(self):
        last_dag_run = self.last_run()

        if last_dag_run:
            dag_task_execution_date = self.previous_schedule(last_dag_run.execution_date)
            print dag_task_execution_date

            if dag_task_execution_date.date() != last_dag_run.execution_date.date():
                dag_task_execution_date = datetime.combine(
                    last_dag_run.execution_date.date(),
                    dag_task_execution_date.time()
                )

            print dag_task_execution_date
            print last_dag_run.execution_date

            if dag_task_execution_date != last_dag_run.execution_date:
                session = settings.Session

                dag_re_schedule_run = models.DagRun(
                    dag_id=self.dag_id,
                    run_id='scheduled__' + dag_task_execution_date.isoformat(),
                    execution_date=dag_task_execution_date,
                    start_date=datetime.now(),
                    end_date=datetime.now(),
                    state=State.SUCCESS,
                    external_trigger=False
                )
                session.add(dag_re_schedule_run)
                session.commit()

                for dag_task_id in self.task_ids:
                    task_instance = models.TaskInstance(
                        self.get_task(dag_task_id),
                        execution_date=dag_task_execution_date,
                        state=State.SUCCESS
                    )
                    task_instance.start_date = datetime.now()
                    task_instance.end_date = datetime.now()

                    session.add(task_instance)
                    session.commit()

    def last_run(self):
        session = settings.Session
        dag_run = models.DagRun

        last_dag_run = session.query(
            dag_run.id,
            dag_run.dag_id,
            dag_run.execution_date
        ).filter(dag_run.dag_id == self.dag_id) \
            .order_by(dag_run.id.desc()) \
            .limit(1) \
            .one_or_none()

        return last_dag_run
