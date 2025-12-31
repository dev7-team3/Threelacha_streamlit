"""지역별 가격비교 쿼리 생성 모듈"""

from typing import Optional
from datetime import date
from .query_utils import build_where_country_clause
from data.connection import DatabaseConnection
import pandas as pd


def get_country_list(conn: DatabaseConnection = None) -> pd.DataFrame:
    """
    mart_price_drop_top3에서 사용 가능한 지역 목록 조회
    """
    database, user = conn.get_config()
    query = f"""
    SELECT DISTINCT country_nm FROM {database}.mart_price_drop_top3
    """

    return query.strip()


def get_price_drop_top3_query(
    country_filter: Optional[str] = None,
    # limit: Optional[int] = 4
    conn: DatabaseConnection = None,
) -> str:
    """
    전일 대비 가격 하락율이 높은 상품 리스트 쿼리를 생성합니다.

    Args:
        country_filter: 지역 필터
        limit: 결과 제한 개수 (None이면 제한 없음)

    Returns:
        str: SQL 쿼리 문자열
    """
    where_sql = build_where_country_clause(country_filter)
    #    limit_clause = f"LIMIT {limit}" if limit else ""
    database, user = conn.get_config()
    query = f"""
    SELECT
        item_nm,
        kind_nm,
        product_cls_unit,
        base_dt,
        base_pr,
        prev_1d_dt,
        prev_1d_pr,
        prev_1d_dir_pct
    FROM {database}.mart_price_drop_top3
    {where_sql}
    ORDER BY ranking
    """

    return query.strip()


def get_price_rise_top3_query(
    country_filter: Optional[str] = None,
    conn: DatabaseConnection = None,
) -> str:
    """
    전일 대비 가격 상승률이 높은 상품 리스트 쿼리를 생성합니다.

    Args:
        country_filter: 지역 필터

    Returns:
        str: SQL 쿼리 문자열
    """
    where_sql = build_where_country_clause(country_filter)
    database, user = conn.get_config()

    query = f"""
    SELECT
        item_nm,
        kind_nm,
        product_cls_unit,
        base_dt,
        base_pr,
        prev_1d_dt,
        prev_1d_pr,
        prev_1d_dir_pct
    FROM {database}.mart_price_rise_top3
    {where_sql}
    ORDER BY ranking
    """

    return query.strip()
