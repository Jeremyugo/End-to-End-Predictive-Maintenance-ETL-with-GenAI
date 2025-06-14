import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from pyspark.sql import SparkSession
from utils.config import S3_ACCESS_KEY, S3_ENDPOINT_URL, S3_SECRET_KEY, path_to_spark_jars

def create_spark_session(storage: str = 'local') -> SparkSession:
    """
    Create a Spark session for local or S3 storage.

    Args:
        storage (str): Storage type ('local' or 's3').

    Returns:
        SparkSession: Configured Spark session.
    """
    if storage == 'local':
        spark = (
            SparkSession.builder
            .appName('iot_data_ingestion')
            .getOrCreate()
        )
        
    elif storage == 's3':
        spark = (
            SparkSession.builder
            .appName("S3-Delta-Stream")
            .config("spark.jars", path_to_spark_jars)
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .config("spark.hadoop.fs.s3a.endpoint", S3_ENDPOINT_URL)
            .config("spark.hadoop.fs.s3a.access.key", S3_ACCESS_KEY)
            .config("spark.hadoop.fs.s3a.secret.key", S3_SECRET_KEY)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .getOrCreate()
        )
        
    return spark