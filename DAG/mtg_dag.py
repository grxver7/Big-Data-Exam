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

import os
import logging

args = {
    'owner': 'airflow'
}

# Shared configurations
HDFS_RAW_DIR = "/user/hadoop/data/raw"
HDFS_BRONZE_DIR = "/user/hadoop/data/bronze"
HDFS_SILVER_DIR = "/user/hadoop/data/silver"
LOCAL_RAW_FILE = os.path.expanduser("~/raw_data/mtg_data.json")

# DAG definition
dag = DAG('MTG_DAG', default_args=args, description='MTG_DAG',
          schedule_interval='56 18 * * *',
          start_date=datetime(2019, 10, 16), catchup=False, max_active_runs=1)

# Helper functions
def delete_hdfs_file(hdfs_file):
    """Delete file in HDFS if it exists."""
    logging.info(f"Deleting HDFS file if exists: {hdfs_file}")
    os.system(f"hadoop fs -rm -f {hdfs_file}")

def upload_file_to_hdfs(local_file, hdfs_file):
    """Upload a local file to HDFS."""
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"Local file {local_file} does not exist.")
    logging.info(f"Uploading {local_file} to {hdfs_file}")
    os.system(f"hadoop fs -put {local_file} {hdfs_file}")

# Tasks
create_raw_directory = CreateDirectoryOperator(
    task_id='create_raw_directory',
    path='/home/airflow',
    directory='raw_mtg',
    dag=dag
)

create_hdfs_raw_dir_task = HdfsMkdirFileOperator(
    task_id='create_hdfs_raw_directory',
    directory=HDFS_RAW_DIR,
    hdfs_conn_id='hdfs',
    dag=dag
)

create_hdfs_bronze_dir_task = HdfsMkdirFileOperator(
    task_id='create_hdfs_bronze_directory',
    directory=HDFS_BRONZE_DIR,
    hdfs_conn_id='hdfs',
    dag=dag
)

create_hdfs_silver_dir_task = HdfsMkdirFileOperator(
    task_id='create_hdfs_silver_directory',
    directory=HDFS_SILVER_DIR,
    hdfs_conn_id='hdfs',
    dag=dag
)

clear_old_local_data_task = ClearDirectoryOperator(
    task_id='clear_local_raw_dir',
    directory='/home/airflow/raw_mtg',
    pattern='*',
    dag=dag,
)

clear_hdfs_raw_dir_task = HdfsPutFileOperator(
    task_id='delete_hdfs_raw_dir',
    local_file=None,
    remote_file=HDFS_RAW_DIR,
    overwrite=True,
    hdfs_conn_id='hdfs',
    dag=dag
)

upload_to_hdfs_task = DummyOperator(
    task_id='upload_to_hdfs',
    dag=dag
)

collect_job_mtg = SparkSubmitOperator(
    task_id='collect_job_mtg',
    application='/home/airflow/airflow/python/collect_job_mtg.py',
    conn_id='spark_default',
    total_executor_cores=2,
    executor_cores=2,
    executor_memory='2g',
    driver_memory='4g',
    num_executors=2,
    application_args=[
        '--hdfs_source_dir', HDFS_RAW_DIR,
        '--hdfs_target_dir', HDFS_BRONZE_DIR,
        '--hdfs_target_format', 'json'
    ],
    dag=dag
)

bronze_job_mtg = SparkSubmitOperator(
    task_id='bronze_job_mtg',
    conn_id='spark',
    application='/home/airflow/airflow/python/bronze_job_mtg.py',
    total_executor_cores='2',
    executor_cores='2',
    executor_memory='2g',
    driver_memory='4g',
    num_executors='2',
    application_args=['--hdfs_source_dir', '/user/hadoop/data/raw', '--hdfs_target_dir', '/user/hadoop/data/bronze', '--hdfs_target_format', 'parquet'],
    dag = dag
)

silver_job_mtg = SparkSubmitOperator(
    task_id='silver_job_mtg',
    conn_id='spark',
    application='/home/airflow/airflow/python/silver_job_mtg.py',
    total_executor_cores='2',
    executor_cores='2',
    executor_memory='2g',
    driver_memory='4g',
    num_executors='2',
    name='spark_calculate_top_tvseries',
    application_args=['--hdfs_source_dir', '/user/hadoop/data/bronze', '--hdfs_target_dir', '/user/hadoop/data/silver', '--hdfs_target_format', 'parquet'],
    dag = dag
)

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

# Task dependencies
create_hdfs_raw_dir_task >> clear_old_local_data_task >> clear_hdfs_raw_dir_task >> upload_to_hdfs_task >> collect_job_mtg
collect_job_mtg >> bronze_job_mtg
bronze_job_mtg >> silver_job_mtg
silver_job_mtg >> ingestDB_job_mtg