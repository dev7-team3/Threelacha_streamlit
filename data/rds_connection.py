"""RDS 데이터베이스 연결 모듈"""

import os
import time
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from data.connection import DatabaseConnection
from data.logger import setup_logger

logger = setup_logger("rds_connection")


class RDSConnection(DatabaseConnection):
    """RDS 데이터베이스 연결 클래스"""

    def __init__(self):
        self._engine = None
        self._database = os.getenv("RDS_DB")
        self._schema = os.getenv("RDS_SCHEMA")
        self._host = os.getenv("RDS_HOST")
        self._port = os.getenv("RDS_PORT", "5432")
        self._user = os.getenv("RDS_USER")
        logger.info(
            f"RDSConnection 초기화: host={self._host}, database={self._database}, schema={self._schema}"
        )

    def get_config(self) -> tuple[str, str]:
        """RDS 설정을 반환합니다.

        Returns:
            tuple[str, str]: database, host
        """
        return self._schema, self._database

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
        start_time = time.time()
        connection_type = "rds"

        logger.info(f"[{connection_type}] 쿼리 실행 시작")
        logger.debug(f"[{connection_type}] 쿼리: {query[:200]}...")  # 처음 200자만 로깅

        engine = self._get_engine()

        try:
            df = pd.read_sql(query, engine)
            total_time = time.time() - start_time

            logger.info(
                f"[{connection_type}] 쿼리 완료 - "
                f"총 시간: {total_time:.2f}초, "
                f"행 수: {len(df)}"
            )

            # Streamlit 세션 상태에 성능 정보 저장
            if "query_performance" not in st.session_state:
                st.session_state.query_performance = []

            st.session_state.query_performance.append({
                "connection_type": connection_type,
                "total_time": total_time,
                "wait_time": 0,  # RDS는 대기 시간이 없음
                "fetch_time": total_time,
                "row_count": len(df),
                "query_preview": query[:100],
            })

            return df
        except Exception as e:
            error_msg = f"RDS 쿼리 실행 중 오류: {e!s}"
            logger.error(f"[{connection_type}] {error_msg}", exc_info=True)
            raise Exception(error_msg) from e
