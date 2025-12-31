import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def get_rds_engine():
    user = os.getenv("RDS_USER")
    password = os.getenv("RDS_PASSWORD")
    host = os.getenv("RDS_HOST")
    port = os.getenv("RDS_PORT", "5432")
    db = os.getenv("RDS_DB")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def execute_rds_query(sql: str) -> pd.DataFrame:
    engine = get_rds_engine()
    return pd.read_sql(sql, engine)
