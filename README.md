# py-airflow

The aim of this repo is a POC that adding a simple layer on top of airflow package will give a huge advantage when we work with airflow.

## Problem

While I was working with airflow in my company I have found that we were repeating the same logics in most of our DAGs. They were simple logic, such as execute an impala invalidate command, hive command to refresh a table, and others command a little bit more complex such as execute spark with some configuration and options.

Recently I have found another problem when I was re-scheduling the DAGs. Airflow doesn't provide out of the box an easy way to re-schedule a DAG. After googling the issue I've found, to be able to re-schedule a DAGs it is necessary to create a new DAG with the new schedule, but this solution has a problem too, you lose the track of the DAGs and in case you will need to re-run a date in the past, you end up with another problem. Along with the re-scheduling problem I have found another issue with the sensor. To define an external sensor you have to specify the delta time for the sensor (the time different between the execution of the DAG and the execution of the DAG sensed) and in case you want to re-schedule the DAG you might screw up other DAGs, making the process really painful.


## Solution

 - Create a layer on top of airflow operators we are using to encapsulate the repeat logic.
 - Make the external sensor operator decouple from the delta time.
 - Add a functionality to allow to re-schedule the current DAG without create a new one and loose the DAG track.
 
 
## POC

**What we can found in the POC?**

In this POC you can find a simple example where to prove how easy is to create a DAG that has an external sensor which you can easily re-scheduler it without having in consideration the delta time and without repeat your self.

**How to access airflow UI?**

Once you have you container up you can access to the airflow webserver `http://127.0.0.1:8080/`. You can change the port editing the docker-compose.yml.


Lets start with the demo.

1. **Setup**

    In order to get the POC set up and running please run the following commands:
    
    ```
    $ git clone https://github.com/dohernandez/py-airflow.git
    $ cd py-airflow
    $ make airflow-run
    ```

2. **Turn on the DAGs**
    
    - Access to the airflow UI throughout your browser.
    - Turn on the DAGs.
    
    Notice that even turning un your DAGs nothing will happen. This is because we haven't start the scheduler daemon.
    
3. **Start scheduler daemon**

    To start the scheduler daemon you **MUST** have started the containers. Look at the step 1.
    
    ```
    $ make airflow-scheduler-run
    ```
    
    Once you start the scheduler you will notice that it will start to schedule each DAGs.
    
4. **Re-schedule a DAG**
    
    Re-schedule a DAG is way more easy than before. Now you just need to call a function and it will do all the job for you.
    
    - Open/Edit the DAG file `demo/etl-sensor-dag/dags/test_external_sensor_dag.py
    - Uncomment the line `# dag.re_scheduler('40 17 * * *')`
    - Clean up some dates in the DAG
    - Let the scheduler do it jobs
    
    Notice that the new run will execute using the new scheduler and it will automatically calculate the new delta time for the the external sensor.


## Benefit
   - Single source of truth for the logic implemented when create a DAG.
   - External sensor only depends on DAG - Task and not anymore in hardcoded delta time.
   - Easy way to re-schedule DAG at any time.