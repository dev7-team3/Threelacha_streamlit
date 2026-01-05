from data.connection import DatabaseConnection


def get_update_status_query(conn: DatabaseConnection = None) -> str:
    """
    대시보드 메타 정보 (최신 업데이트 상태) 조회 쿼리
    - 최신 업데이트 날짜
    - 업데이트된 품목 수
    - 업데이트된 지역 수
    """
    database, user = conn.get_config()
    return f"""
        SELECT
            latest_date,
            row_count,
            country_count
        FROM {database}.mart_update_status
    """
