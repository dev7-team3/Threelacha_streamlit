"""RDS 데이터베이스 연결 모듈"""

import os
import pandas as pd
from sqlalchemy import create_engine
from data.connection import DatabaseConnection


class RDSConnection(DatabaseConnection):
    """RDS 데이터베이스 연결 클래스"""

    def __init__(self):
        self._engine = None
        self._database = os.getenv("RDS_DB")
        self._host = os.getenv("RDS_HOST")
        self._port = os.getenv("RDS_PORT", "5432")
        self._user = os.getenv("RDS_USER")

    def get_config(self) -> tuple[str, str]:
        """RDS 설정을 반환합니다.

        Returns:
            tuple[str, str]: database, host
        """
        return self._database, self._user

    def _get_engine(self):
        """RDS 엔진을 생성하고 반환합니다."""
        if self._engine is None:
            user = os.getenv("RDS_USER")
            password = os.getenv("RDS_PASSWORD")
            host = os.getenv("RDS_HOST")
            port = os.getenv("RDS_PORT", "5432")
            db = os.getenv("RDS_DB")

            url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
            self._engine = create_engine(url)

        return self._engine

    def execute_query(self, query: str, **kwargs) -> pd.DataFrame:
        """RDS 쿼리를 실행하고 DataFrame으로 반환합니다.

        Args:
            query: 실행할 SQL 쿼리 문자열
            **kwargs: 추가 파라미터 (사용되지 않지만 호환성을 위해 유지)

        Returns:
            pd.DataFrame: 쿼리 결과를 담은 DataFrame
        """
        engine = self._get_engine()
        return pd.read_sql(query, engine)
