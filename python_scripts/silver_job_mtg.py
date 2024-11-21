#!/usr/bin/env python
# coding: utf-8
import pyspark
from pyspark.sql import SparkSession
import argparse
from pyspark.sql.functions import col, explode

def get_args():
    """
    Parses Command Line Args
    """
    parser = argparse.ArgumentParser(description='Optimized Spark Job for processing Magic: The Gathering data in HDFS.')
    parser.add_argument('--hdfs_source_dir', help='HDFS source directory, e.g. /user/hadoop/data/bronze', required=True, type=str)
    parser.add_argument('--hdfs_target_dir', help='HDFS target directory, e.g. /user/hadoop/data/silver', required=True, type=str)
    parser.add_argument('--hdfs_target_format', help='HDFS target format, e.g. csv or parquet or...', required=True, type=str)
    
    return parser.parse_args()

if __name__ == '__main__':
    # Parse Command Line Args
    args = get_args()

    # Initialize Spark Context and Session
    sc = pyspark.SparkContext()
    spark = SparkSession(sc)

    # Create the 'silver' database if it does not exist
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")

    # Define HDFS paths
    bronze_hdfs_path = args.hdfs_source_dir
    silver_hdfs_path = args.hdfs_target_dir

    # Load and clean bronze data
    df_bronze = spark.read.parquet(bronze_hdfs_path).dropDuplicates()

    # Cache the cleaned data for reuse (improves performance on subsequent actions)
    df_silver = df_bronze.cache()

    # Partition the data upfront for optimal writing
    df_silver = df_silver.repartition(20)  # Adjust number of partitions based on data size

    # 1. Card Table: Main table for card properties
    card_df = df_silver.select(
        col("id").alias("card_id"),
        "name", "mana_cost", "cmc", "type", "rarity", "text", "power", "toughness", 
        "artist", "image_url", "set", "set_name"
    ).dropDuplicates()

    # Write Card Data to Silver Table, partition by 'set' to improve query performance
    card_df.write.mode("overwrite").partitionBy("set").option("path", f"{silver_hdfs_path}/cards").saveAsTable("silver.cards")

    # 2. Foreign Names Table: Multilingual names and text
    foreign_names_df = (
        df_silver.select("id", explode("foreign_names").alias("foreign_name_info"))
        .select(
            col("id").alias("card_id"),
            col("foreign_name_info.name").alias("foreign_name"),
            col("foreign_name_info.language"),
            col("foreign_name_info.text").alias("foreign_text"),
            col("foreign_name_info.type").alias("foreign_type"),
            col("foreign_name_info.flavor"),
            col("foreign_name_info.imageUrl").alias("foreign_image_url")
        )
        .dropDuplicates()
    )

    foreign_names_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/foreign_names").saveAsTable("silver.foreign_names")

    # 3. Legality Table: Game formats and legality
    legalities_df = (
        df_silver.select("id", explode("legalities").alias("legality_info"))
        .select(
            col("id").alias("card_id"),
            col("legality_info.format"),
            col("legality_info.legality")
        )
        .dropDuplicates()
    )

    legalities_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/legalities").saveAsTable("silver.legalities")

    # 4. Printings Table: Sets in which the card appeared
    printings_df = (
        df_silver.select("id", explode("printings").alias("set_code"))
        .select(
            col("id").alias("card_id"),
            "set_code"
        )
        .dropDuplicates()
    )

    printings_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/printings").saveAsTable("silver.printings")

    # Stop Spark session
    spark.stop()
