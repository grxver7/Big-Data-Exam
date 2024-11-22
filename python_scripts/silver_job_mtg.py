#!/usr/bin/env python
# coding: utf-8
import pyspark
from pyspark.sql import SparkSession
import argparse
from pyspark.sql.functions import desc
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, explode


def get_args():
    """
    Parses Command Line Args
    """
    parser = argparse.ArgumentParser(description='Some Basic Spark Job doing some stuff on IMDb data stored within HDFS.')
    parser.add_argument('--hdfs_source_dir', help='HDFS source directory, e.g. /user/hadoop/data/bronze', required=True, type=str)
    parser.add_argument('--hdfs_target_dir', help='HDFS target directory, e.g. /user/hadoop/data/silver', required=True, type=str)
    parser.add_argument('--hdfs_target_format', help='HDFS target format, e.g. csv or parquet or...', required=True, type=str)
    
    return parser.parse_args()

if __name__== '__main__':
    
    # Parse Command Line Args
    args = get_args()
    
        # Initialize Spark Context
    sc = pyspark.SparkContext()
    spark = SparkSession(sc)
    
    # Create the 'silver' database if it does not exist
    spark.sql("CREATE DATABASE IF NOT EXISTS silver")
    
    # Pfade für die HDFS Layer definieren
    bronze_hdfs_path = args.hdfs_source_dir
    silver_hdfs_path = args.hdfs_target_dir

    # Load bronze data
    df_bronze = spark.read.parquet(bronze_hdfs_path)
    
    # Clean data: Remove duplicates
    df_silver = df_bronze.dropDuplicates()
    
    # 1. Card Table: Main table for card properties
    card_df = df_silver.select(
        col("id").alias("card_id"),
        "name", "mana_cost", "cmc", "type", "rarity", "text", "power", "toughness", 
        "artist", "image_url", "set", "set_name"
        ).dropDuplicates()
    
    # Write to HDFS with path specified for the "cards" table
    card_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/cards").saveAsTable("silver.cards")
    
    # 2. Foreign Names Table: Multilingual names and text
    foreign_names_df = df_silver.select("id", explode("foreign_names").alias("foreign_name_info"))     .select(
        col("id").alias("card_id"),
        col("foreign_name_info.name").alias("foreign_name"),
        col("foreign_name_info.language"),
        col("foreign_name_info.text").alias("foreign_text"),
        col("foreign_name_info.type").alias("foreign_type"),
        col("foreign_name_info.flavor"),
        col("foreign_name_info.imageUrl").alias("foreign_image_url")
    ).dropDuplicates()
    
    # Write to HDFS with path specified for the "foreign_names" table
    foreign_names_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/foreign_names").saveAsTable("silver.foreign_names")
    
    # 3. Legality Table: Game formats and legality
    legalities_df = df_silver.select("id", explode("legalities").alias("legality_info"))     .select(
        col("id").alias("card_id"),
        col("legality_info.format"),
        col("legality_info.legality")
    ).dropDuplicates()
    
    # Write to HDFS with path specified for the "legalities" table
    legalities_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/legalities").saveAsTable("silver.legalities")
    
    # 4. Printings Table: Sets in which the card appeared
    printings_df = df_silver.select("id", explode("printings").alias("set_code"))     .select(
        col("id").alias("card_id"),
        "set_code"
    ).dropDuplicates()
    
    # Write to HDFS with path specified for the "printings" table
    printings_df.write.mode("overwrite").option("path", f"{silver_hdfs_path}/printings").saveAsTable("silver.printings")
    
    spark.stop()