import pytest
from pyspark.sql import SparkSession

@pytest.fixture
def spark():
    return SparkSession.builder.appName("test").getOrCreate()

def test_spark_session(spark):
    assert spark is not None
    assert spark.sparkContext.appName == "test"

def test_dataframe_creation(spark):
    data = [("Alice", 25), ("Bob", 30)]
    df = spark.createDataFrame(data, ["name", "age"])
    assert df.count() == 2