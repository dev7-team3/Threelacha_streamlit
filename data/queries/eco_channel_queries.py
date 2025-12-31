"""친환경 관련 쿼리 생성 모듈"""

from data.connection import DatabaseConnection


def get_latest_price_statistics_query(conn: DatabaseConnection = None) -> str:
    """최신 가격 통계 데이터를 조회하는 쿼리를 생성합니다.

    Args:
        category_filter: 카테고리 필터

    Returns:
        str: SQL 쿼리 문자열
    """
    database, user = conn.get_config()

    query = f"""
    WITH latest_date AS (
        SELECT MAX(res_dt) as max_date
        FROM {database}.mart_eco_price_statistics_by_category
    )
    SELECT 
        res_dt,
        item_cd,
        item_nm,
        market_category,
        record_count,
        avg_price,
        min_price,
        max_price
    FROM {database}.mart_eco_price_statistics_by_category
    CROSS JOIN latest_date
    WHERE res_dt = latest_date.max_date
    ORDER BY item_nm, market_category, avg_price
    """

    return query.strip()
