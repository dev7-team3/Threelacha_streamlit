"""채널별 쿼리 생성 모듈"""

from typing import Optional
from datetime import date
from .query_utils import build_where_clause
from data.connection import DatabaseConnection


def get_channel_comparison_query(
    category_filter: Optional[str] = None,
    limit: Optional[int] = None,
    conn: DatabaseConnection = None,
) -> str:
    """유통 vs 전통 채널별 가격 비교 쿼리를 생성합니다.

    Args:
        date_filter: 날짜 필터 (None이면 최신 날짜 자동 조회)
        category_filter: 카테고리 필터
        limit: 결과 제한 개수 (None이면 제한 없음)

    Returns:
        str: SQL 쿼리 문자열
    """
    limit_clause = f"LIMIT {limit}" if limit else ""
    database, user = conn.get_config()
    query = f"""
    WITH latest_date AS (
        SELECT MAX(res_dt) as max_date
        FROM {database}.mart_retail_channel_comparison
    ),
    aggregated_data AS (
        SELECT 
            item_nm,
            kind_nm,
            channel_type,
            AVG(avg_price) as avg_price,
            SUM(record_count) as total_records
        FROM {database}.mart_retail_channel_comparison
        CROSS JOIN latest_date
        WHERE res_dt = latest_date.max_date
        {f"AND category_nm = '{category_filter}'" if category_filter and category_filter != "전체" else ""}
        GROUP BY item_nm, kind_nm, channel_type
        HAVING item_nm IS NOT NULL
    )
    SELECT 
        (SELECT max_date FROM latest_date) as "조회일자",
        item_nm,
        kind_nm,
        MAX(CASE WHEN channel_type = '유통' THEN avg_price END) as "유통_평균가격",
        MAX(CASE WHEN channel_type = '전통' THEN avg_price END) as "전통_평균가격",
        MAX(CASE WHEN channel_type = '유통' THEN avg_price END) - 
        MAX(CASE WHEN channel_type = '전통' THEN avg_price END) as "가격차이",
        MAX(CASE WHEN channel_type = '유통' THEN total_records END) as "유통_레코드수",
        MAX(CASE WHEN channel_type = '전통' THEN total_records END) as "전통_레코드수"
    FROM aggregated_data
    CROSS JOIN latest_date
    GROUP BY item_nm, kind_nm
    HAVING MAX(CASE WHEN channel_type = '유통' THEN avg_price END) IS NOT NULL
        AND MAX(CASE WHEN channel_type = '전통' THEN avg_price END) IS NOT NULL
    ORDER BY ABS(MAX(CASE WHEN channel_type = '유통' THEN avg_price END) - 
                MAX(CASE WHEN channel_type = '전통' THEN avg_price END)) DESC
    {limit_clause}
    """

    return query.strip()


def get_channel_stats_query(
    date_filter: Optional[date] = None,
    category_filter: Optional[str] = None,
    conn: DatabaseConnection = None,
) -> str:
    """채널별 통계 쿼리를 생성합니다.

    Args:
        date_filter: 날짜 필터
        category_filter: 카테고리 필터

    Returns:
        str: SQL 쿼리 문자열
    """
    where_sql = build_where_clause(date_filter, category_filter)
    database, user = conn.get_config()

    query = f"""
    SELECT 
        item_nm,
        kind_nm,
        channel_type,
        AVG(avg_price) as "평균가격",
        MIN(min_price) as "최저가격",
        MAX(max_price) as "최고가격",
        SUM(record_count) as "총레코드수"
    FROM {database}.mart_retail_channel_comparison
    {where_sql}
    GROUP BY item_nm, kind_nm, channel_type
    ORDER BY item_nm, kind_nm, channel_type
    """

    return query.strip()
