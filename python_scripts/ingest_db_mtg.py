#!/usr/bin/env python
# coding: utf-8

import argparse
import psycopg2
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd


def get_args():
    """
    Parses Command Line Args
    """
    parser = argparse.ArgumentParser(description='Spark Job to process and load data from HDFS into PostgreSQL.')
    parser.add_argument('--hdfs_source_dir', help='HDFS source directory, e.g. /user/hadoop/data/silver', required=True, type=str)
    parser.add_argument('--hdfs_target_format', help='HDFS target format, e.g. csv or parquet or...', required=True, type=str)
    parser.add_argument('--postgres_host', help='PostgreSQL host (e.g., localhost)', required=True, type=str)
    parser.add_argument('--postgres_port', help='PostgreSQL port', default='5432', type=str)
    parser.add_argument('--postgres_db', help='PostgreSQL database name', required=True, type=str)
    parser.add_argument('--postgres_table', help='Target table in PostgreSQL', required=True, type=str)
    parser.add_argument('--postgres_user', help='PostgreSQL username', required=True, type=str)
    parser.add_argument('--postgres_password', help='PostgreSQL password', required=True, type=str)

    return parser.parse_args()

# Check and create database if it doesn't exist
def create_database_if_not_exists(db_name, conn):
    # Set autocommit mode for the connection
    conn.autocommit = True
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
            if not cursor.fetchone():
                print(f"Database '{db_name}' does not exist. Creating it now.")
                cursor.execute(f"CREATE DATABASE {db_name};")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        # Reset autocommit to False after creating the database
        conn.autocommit = False

def create_postgres_table_if_not_exists(df, table_name, conn):
    type_mapping = {
        'string': 'TEXT',
        'int': 'INTEGER',
        'long': 'BIGINT',
        'float': 'FLOAT',
        'double': 'DOUBLE PRECISION',
        'boolean': 'BOOLEAN',
        'timestamp': 'TIMESTAMP',
    }

    columns = []
    for col_name, dtype in df.dtypes:
        postgres_dtype = type_mapping.get(dtype, 'TEXT')
        # Add primary key constraint for card_id
        if col_name == 'card_id':
            columns.append(f"{col_name} {postgres_dtype} PRIMARY KEY")
        else:
            columns.append(f"{col_name} {postgres_dtype} NULL")

    create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
    
    with conn.cursor() as cursor:
        cursor.execute(create_query)
        conn.commit()
    
    print(f"Table {table_name} ensured in PostgreSQL.")

    
def escape_single_quotes(value):
  """
  Escapes single quotes and backslashes in string fields to avoid SQL syntax errors.
  """
  if isinstance(value, str):
    return value.replace("'", "''").replace("\\", "\\\\")  # Escape both single quotes and backslashes
  return value  

def write_data_to_postgres(df, table_name, conn):
    # Convert the PySpark DataFrame to a Pandas DataFrame for easier insertion
    df_pandas = df.toPandas()

    # Create a cursor object to interact with PostgreSQL
    cursor = conn.cursor()

    # Prepare the columns and values for the insert query
    columns = ', '.join(df_pandas.columns)
    
    for index, row in df_pandas.iterrows():
        # Escape values to prevent SQL injection and handle NULLs
        values = ', '.join([
            f"NULL" if pd.isnull(v) else f"'{escape_single_quotes(v)}'" if isinstance(v, str) else str(v)
            for v in row.values
        ])
        
        # Create the insert query with ON CONFLICT handling
        insert_query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({values})
            ON CONFLICT (card_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                text = EXCLUDED.text,
                artist = EXCLUDED.artist,
                image_url = EXCLUDED.image_url;
        """
        
        try:
            cursor.execute(insert_query)
        except psycopg2.ProgrammingError as e:
            print(f"Error inserting row {row}: {e}")
            conn.rollback()
            raise
        except psycopg2.IntegrityError as e:
            print(f"Integrity error inserting row {row}: {e}")
            conn.rollback()
            raise

    # Commit changes and close cursor
    conn.commit()
    cursor.close()
    print(f"Data successfully inserted into {table_name}.")

if __name__ == '__main__':
    # Parse Command Line Args
    args = get_args()

    # Connect to PostgreSQL using psycopg2
    try:
        # Connect to default database to create target database if needed
        default_conn = psycopg2.connect(
            host=args.postgres_host,
            port=args.postgres_port,
            database="postgres",
            user=args.postgres_user,
            password=args.postgres_password
        )
        create_database_if_not_exists(args.postgres_db, default_conn)
        default_conn.close()

        # Now connect to the target database
        conn = psycopg2.connect(
            host=args.postgres_host,
            port=args.postgres_port,
            database=args.postgres_db,
            user=args.postgres_user,
            password=args.postgres_password
        )
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        exit(1)


    # Initialize Spark session
    spark = SparkSession.builder.appName("LoadDataToPostgres").getOrCreate()

    # HDFS source path for silver layer data
    silver_hdfs_path = args.hdfs_source_dir

    # Load Silver data
    silver_cards_hdfs_path = f"{silver_hdfs_path}/cards"
    df_silver_cards = spark.read.parquet(silver_cards_hdfs_path)

    # Select required fields and drop duplicates
    df_card = df_silver_cards.select(
        col("card_id"),
        col("name"),
        col("text"),
        col("artist"),
        col("image_url")
    ).dropDuplicates()

    create_database_if_not_exists(args.postgres_table, conn)

    # Ensure the table exists in PostgreSQL
    # Ensure the table exists in PostgreSQL
    create_postgres_table_if_not_exists(df_card, args.postgres_table, conn)

    # Load the data into PostgreSQL
    write_data_to_postgres(df_card, args.postgres_table, conn)

    # Close PostgreSQL connection and Spark session
    conn.close()
    spark.stop()
