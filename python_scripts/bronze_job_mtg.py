#!/usr/bin/env python
# coding: utf-8
import pyspark
from pyspark.sql import SparkSession
from pyspark import SparkContext
import argparse
from pyspark.sql.functions import desc
import subprocess

def get_args():
    """
    Parses Command Line Args
    """
    parser = argparse.ArgumentParser(description='Some Basic Spark Job doing some stuff on IMDb data stored within HDFS.')
    parser.add_argument('--hdfs_source_dir', help='HDFS source directory, e.g. /user/hadoop/data/raw', required=True, type=str)
    parser.add_argument('--hdfs_target_dir', help='HDFS target directory, e.g. /user/hadoop/data/bronze', required=True, type=str)
    parser.add_argument('--hdfs_target_format', help='HDFS target format, e.g. csv or parquet or...', required=True, type=str)
    
    return parser.parse_args()

if __name__== '__main__':
        # Parse Command Line Args
    args = get_args()

    # Initialize Spark Context
    sc = pyspark.SparkContext()
    spark = SparkSession(sc)

    print("Spark session initialized")

    # Load the JSON data
    df_mtg_data_json = spark.read     .format('json')     .option('multiline', 'true')     .option('inferSchema', 'true')     .load(args.hdfs_source_dir)

    # Check if the path exists, and create it if it doesn't
    path_check_command = f"hadoop fs -test -d {args.hdfs_target_dir}"
    path_check_result = subprocess.run(path_check_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if path_check_result.returncode != 0:
        create_dir_command = f"hadoop fs -mkdir -p {args.hdfs_target_dir}"
        subprocess.run(create_dir_command, shell=True)
        print(f"Created directory: {args.hdfs_target_dir}")
    else:
        print(f"Directory {args.hdfs_target_dir} already exists.")

    # Repartition and save the DataFrame as Parquet
    df_mtg_data_json     .repartition(10)     .write     .mode("overwrite")     .format("parquet")     .option('path', args.hdfs_target_dir)     .partitionBy('set_name')     .save()
    
    print(f"Directory {args.hdfs_target_dir} already exists.")

    spark.stop()