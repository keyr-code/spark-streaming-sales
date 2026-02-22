import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="module")
def spark():
    """Create Spark session for integration tests"""
    spark = (
        SparkSession.builder.appName("IntegrationTest").master("local[2]").getOrCreate()
    )
    yield spark
    spark.stop()


def test_spark_session(spark):
    """Test Spark session creation"""
    assert spark is not None
    assert spark.sparkContext.appName == "IntegrationTest"


def test_spark_dataframe_operations(spark):
    """Test basic Spark DataFrame operations"""
    data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
    columns = ["name", "age"]

    df = spark.createDataFrame(data, columns)

    assert df.count() == 3
    assert len(df.columns) == 2

    filtered_df = df.filter(df.age > 25)
    assert filtered_df.count() == 2
