"""데이터베이스 연결 추상 인터페이스 및 팩토리 모듈"""

from typing import Protocol, Literal
import pandas as pd


class DatabaseConnection(Protocol):
    """데이터베이스 연결 추상 인터페이스"""

    def execute_query(self, query: str, **kwargs) -> pd.DataFrame:
        """쿼리를 실행하고 DataFrame을 반환합니다.

        Args:
            query: 실행할 SQL 쿼리 문자열
            **kwargs: 데이터베이스별 추가 파라미터

        Returns:
            pd.DataFrame: 쿼리 결과를 담은 DataFrame
        """
        ...

    def get_config(self) -> tuple[str, str]:
        """데이터베이스 설정을 반환합니다.

        Returns:
            tuple[str, str]: 데이터베이스 설정
        """
        ...


def get_database_connection(
    db_type: Literal["rds", "athena"] = "athena",
) -> DatabaseConnection:
    """이터베이스 연결 팩토리 함수

    Args:
        db_type: 데이터베이스 타입 ("rds" 또는 "athena")

    Returns:
        DatabaseConnection: 데이터베이스 연결 객체

    Examples:
        >>> # RDS 연결 사용
        >>> conn = get_database_connection("rds")
        >>> df = conn.execute_query("SELECT * FROM table")

        >>> # Athena 연결 사용
        >>> conn = get_database_connection("athena")
    """
    if db_type == "rds":
        from data.rds_connection import RDSConnection

        return RDSConnection()
    elif db_type == "athena":
        from data.athena_connection import AthenaConnection

        return AthenaConnection()
    else:
        raise ValueError(
            f"지원하지 않는 데이터베이스 타입: {db_type}. 'rds' 또는 'athena'를 사용하세요."
        )
