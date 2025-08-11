import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import postgres_config, minio_config, kafka_config

def test_postgres_config():
    assert postgres_config.POSTGRES_CONFIG['host'] == 'pgdatabase'
    assert postgres_config.POSTGRES_CONFIG['database'] == 'goods_store'

def test_minio_config():
    assert 'endpoint' in minio_config.MINIO_CONFIG
    assert 'bucket' in minio_config.MINIO_CONFIG

def test_kafka_config():
    assert kafka_config.DEFAULT_CONFIG['bootstrap_servers'] == 'broker:29092'