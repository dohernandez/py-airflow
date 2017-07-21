import os
from abc import ABCMeta, abstractmethod

from datetime import timedelta

from airflow import configuration as conf
from airflow import models
from airflow.operators.bash_operator import BashOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.operators.sensors import ExternalTaskSensor


class DAGTask(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_task_id(self):
        """
        Method used to generate the id of the task. Each child class should implement this method.
        :return:
        """
        raise NotImplementedError


class BashOperatorDAGTask(BashOperator, DAGTask):
    __metaclass__ = ABCMeta

    def __init__(self, task_id=None, **kwargs):
        super(BashOperatorDAGTask, self).__init__(
            task_id=task_id if task_id else self.generate_task_id(),
            bash_command=self.command(),
            **kwargs
        )

    @abstractmethod
    def command(self):
        """
        Command of the task. Each child class should implement this method.
        :return:
        """
        raise NotImplementedError


class InvalidateImpalaMetadataDAGTask(BashOperatorDAGTask):
    def __init__(self, task_id=None, **kwargs):
        super(InvalidateImpalaMetadataDAGTask, self).__init__(task_id, **kwargs)

    def generate_task_id(self):
        return 'invalidate-metadata'

    def command(self):
        return 'impala-shell -u mapr -q "invalidate metadata;"'


class RefreshImpalaTableDAGTask(BashOperatorDAGTask):
    def __init__(self, database, table, task_id=None, **kwargs):
        if (database is None) ^ (table is None):
            raise ValueError("Please specify both table and database parameters!")

        self.database = database
        self.table = table

        super(RefreshImpalaTableDAGTask, self).__init__(task_id, **kwargs)

    def generate_task_id(self):

        return 'invalidate-metadata-{database}.{table}'.format(database=self.database, table=self.table)

    @property
    def command(self):
        return 'impala-shell -u mapr -q "REFRESH {database}.{table};"'.format(
            database=self.database,
            table=self.table
        )


class ComputeImpalaStatsDAGTask(BashOperatorDAGTask):
    def __init__(self, database, table, task_id=None, **kwargs):
        if (database is None) ^ (table is None):
            raise ValueError("Please specify both table and database parameters!")

        self.database = database
        self.table = table

        super(ComputeImpalaStatsDAGTask, self).__init__(task_id, **kwargs)

    def generate_task_id(self):
        return 'impala-compute-stats-{database}.{table}'.format(database=self.database, table=self.table)

    @property
    def command(self):
        return 'impala-shell -u mapr -q "COMPUTE STATS {database}.{table};"'.format(
            database=self.database,
            table=self.table
        )


class RepairHiveTableDAGTask(HiveOperator, DAGTask):
    def __init__(self, database, table, task_id=None, **kwargs):
        if (database is None) ^ (table is None):
            raise ValueError("Please specify both table and database parameters!")

        self.database = database
        self.table = table

        super(RepairHiveTableDAGTask, self).__init__(
            task_id=task_id if task_id else self.generate_task_id(),
            bash_command=self.command(),
            **kwargs
        )

    def generate_task_id(self):
        return 'hive-repair-{database}.{table}'.format(database=self.database, table=self.table)

    @property
    def command(self):
        return 'USE {database}; MSCK REPAIR TABLE {table};"'.format(
            database=self.database,
            table=self.table
        )


class ExternalTaskSensorDAGTask(ExternalTaskSensor, DAGTask):
    def __init__(self, external_dag_id, external_task_id, timeout=300, task_id=None, **kwargs):
        if (external_dag_id is None) ^ (external_task_id is None):
            raise ValueError("Please specify the external_dag_id and the external_task_id parameters!")

        self.task_id = task_id if task_id else self.generate_task_id()
        self.external_dag_id = external_dag_id
        self.external_task_id = external_task_id

        super(ExternalTaskSensorDAGTask, self).__init__(
            task_id=self.task_id,
            external_dag_id=self.external_dag_id,
            external_task_id=self.external_task_id,
            # time difference between this DAG and the DAG containing the task_id whose
            # execution will poked for success
            execution_delta=timedelta(minutes=0),
            timeout=timeout,
            **kwargs
        )

    def generate_task_id(self):
        return 'external-sensor-{external_dag_id}.{external_task_id}'.format(
            external_dag_id=self.external_dag_id,
            external_task_id=self.external_task_id
        )

    def poke(self, context):
        external_dag = self.dagbag.get_dag(self.external_dag_id)

        self.execution_delta = context['execution_date'] - external_dag.previous_schedule(context['execution_date'])

        return super(ExternalTaskSensorDAGTask, self).poke(context)

    @property
    def dagbag(self):
        return models.DagBag(os.path.expanduser(conf.get('core', 'DAGS_FOLDER')))


class PythonETLDAGTask(BashOperatorDAGTask, DAGTask):
    def __init__(
            self,
            project_setup_name,
            etl,
            etl_task,
            executable_path,
            etl_args=None,
            python_virtual_env_path=None,
            project_name=None,
            task_id=None,
            **kwargs
    ):
        if (project_setup_name is None) ^ (etl is None) ^ (etl_task is None) ^ (executable_path is None):
            raise ValueError("Please specify the project_setup_name, the etl, the etl_task "
                             "and the executable_path parameters!")

        if python_virtual_env_path and (project_name is None):
            raise ValueError("Please specify the project_name parameter "
                             "when the python_virtual_env_path parameters is present!")

        self.project_setup_name = project_setup_name
        self.etl = etl
        self.etl_task = etl_task
        self.executable_path = executable_path
        self.etl_args = etl_args if etl_args else {}
        self.python_virtual_env_path = python_virtual_env_path
        self.project_name = project_name

        super(PythonETLDAGTask, self).__init__(task_id, **kwargs)

    def generate_task_id(self):
        return 'task-{etl_task}'.format(etl_task=self._etl_task)

    @property
    def command(self):
        executable_args = {
            'etl': '{_project_setup_name}.executable.{etl}'.format(
                _project_setup_name=self.project_setup_name,
                etl=self.etl
            ),
            'task': self.etl_task
        }
        executable_args.update(self.etl_args)

        return '{interpreter} {executable_path}/main.py {executable_args}'.format(
            interpreter=self.interpreter,
            executable_path=self.executable_path,
            executable_args=self.resolve_args_dict_to_python_args(executable_args)
        )

    @property
    def interpreter(self):
        interpreter = 'python'

        if self.python_virtual_env_path:
            interpreter = '{python_virtual_env_path}/{project_name}/bin/python'.format(
                python_virtual_env_path=self.python_virtual_env_path,
                project_name=self.project_name
            )
        return interpreter

    @staticmethod
    def resolve_args_dict_to_python_args(args_dictionary):
        """
        :param dict args_dictionary:
        :return:
        """
        if not args_dictionary:
            return ''

        executable_args_array = []

        for arg_name, arg_value in args_dictionary.iteritems():
            executable_args_array.append('--{}'.format(arg_name))
            executable_args_array.append(str(arg_value))

        return ' '.join(executable_args_array)


class SparkETLDAGTask(PythonETLDAGTask):
    def __init__(
            self,
            spark_home,
            spark_master,
            project_setup_name,
            etl,
            etl_task,
            executable_path,
            spark_args=None,
            etl_args=None,
            python_virtual_env_path=None,
            project_name=None,
            task_id=None,
            **kwargs
    ):
        if (spark_home is None) ^ (spark_master is None):
            raise ValueError("Please specify the spark_home, and the spark_master parameters!")

        self.spark_home = spark_home
        self.spark_master = spark_master
        self.spark_args = spark_args

        super(SparkETLDAGTask, self).__init__(
            project_setup_name,
            etl,
            etl_task,
            executable_path,
            etl_args,
            python_virtual_env_path,
            project_name,
            task_id,
            **kwargs
        )

    @property
    def interpreter(self):
        interpreter = ''

        if self.project_name:
            interpreter = 'PYSPARK_PYTHON={python_virtual_envs_path}/{project_name}/bin/python'.format(
                python_virtual_envs_path=self.python_virtual_env_path,
                project_name=self.project_name
            )

        return '{interpreter} {spark_home}/bin/spark-submit --master {spark_master} {spark_args}'.format(
            interpreter=interpreter,
            spark_home=self.spark_home,
            spark_master=self.spark_master,
            spark_args=self.resolve_args_dict_to_python_args(self.spark_args)
        )
