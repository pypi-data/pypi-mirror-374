from datetime import date
from typing import Iterable

from pyspark.sql import DataFrame, SparkSession

from shardate.dates import all_dates_between


def spark_session():
    try:
        return SparkSession.getActiveSession()
    except Exception as e:
        raise RuntimeError("No active SparkSession found. Please create one.") from e


def reader(path):
    spark = spark_session()
    return spark.read.options(basePath=path)


def read_by_date(
    path: str, target_date: date, partition_format="y=%Y/m=%m/d=%d"
) -> DataFrame:
    return reader(path).parquet(f"{path}/{target_date.strftime(partition_format)}")


def read_between(
    path: str, start_date: date, end_date: date, partition_format="y=%Y/m=%m/d=%d"
) -> DataFrame:
    return reader(path).parquet(
        *{
            f"{path}/{i.strftime(partition_format)}"
            for i in all_dates_between(start_date, end_date)
        }
    )


def read_by_dates(
    path: str, dates: Iterable[date], partition_format="y=%Y/m=%m/d=%d"
) -> DataFrame:
    return reader(path).parquet(
        *{f"{path}/{i.strftime(partition_format)}" for i in dates}
    )
