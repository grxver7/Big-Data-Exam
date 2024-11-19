# -*- coding: utf-8 -*-

"""
Title: ETL Workflow for MTG-Cards
Author: Luca Holder
Description: 
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.http_download_operations import HttpDownloadOperator
from airflow.operators.zip_file_operations import UnzipFileOperator
from airflow.operators.hdfs_operations import HdfsPutFileOperator, HdfsGetFileOperator, HdfsMkdirFileOperator
from airflow.operators.filesystem_operations import CreateDirectoryOperator
from airflow.operators.filesystem_operations import ClearDirectoryOperator
from airflow.operators.hive_operator import HiveOperator

args = {
    'owner': 'airflow'
}

dag = DAG('MTG_DAG_ingestDB_only', default_args=args, description='MTG_DAG_File',
          schedule_interval='56 18 * * *',
          start_date=datetime(2019, 10, 16), catchup=False, max_active_runs=1)

ingestDB_job_mtg = SparkSubmitOperator(
    task_id='ingestDB_job_mtg',
    conn_id='spark',
    application='/home/airflow/airflow/python/ingest_db_mtg.py',  # Path to your Spark job
    total_executor_cores='2',
    executor_cores='2',
    executor_memory='2g',
    driver_memory='4g',
    num_executors='2',
    name='spark_ingestDB_process',
    application_args=[
        '--postgres_host', 'postgres',  # PostgreSQL host
        '--postgres_table', 'mtg_db',  # Target table in PostgreSQL
        '--postgres_db', 'postgres',  # PostgreSQL database
        '--postgres_user', 'postgres',  # PostgreSQL username
        '--postgres_password', 'admin',  # PostgreSQL password
        '--hdfs_source_dir', '/user/hadoop/data/silver',  # HDFS source directory
        '--hdfs_target_format', 'parquet',  # Output format (parquet, csv, etc.)
    ],
    config=("spark.jars", "/home/airflow/spark/jars/postgresql-42.5.1.jar"),
    driver_class_path='/home/airflow/spark/jars/postgresql-42.5.4.jar',
    executor_class_path='/home/airflow/spark/jars/postgresql-42.5.4.jar',
    dag=dag
)

ingestDB_job_mtg