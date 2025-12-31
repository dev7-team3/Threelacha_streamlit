"""친환경 페이지 컴포넌트"""

import streamlit as st
import pandas as pd
from data.queries.eco_channel_queries import get_latest_price_statistics_query
from data.connection import DatabaseConnection


def render_market_price_card(
    index: int,
    item_nm: str,
    price_data: dict,
    price_diff: float,
    border_color: str = "#4A90E2",
):
    """여러 마트의 가격을 깔끔하게 표시하는 카드를 렌더링합니다.

    Args:
        item_nm: 품목명
        price_data: {마트명: 가격} 형태의 딕셔너리
        price_diff: 가격 차이
        border_color: 카드 테두리 색상
    """
    # 가격 순으로 정렬
    sorted_markets = sorted(price_data.items(), key=lambda x: x[1])
    cheapest_name, cheapest_price = sorted_markets[0]
    expensive_name, expensive_price = sorted_markets[-1]

    # 카드 컨테이너
    with st.container():
        # 카드 헤더 (품목명)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, {border_color} 0%, {border_color}dd 100%);
                        padding: 15px 20px; border-radius: 10px; margin-bottom: 10px;">
                <h3 style="margin: 0; color: white; font-size: 18px; font-weight: bold;">
                    {index + 1}. {item_nm}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 마트별 가격 표시
        num_markets = len(sorted_markets)

        # 마트 개수에 따라 열 수 결정 (최대 3열)
        num_cols = min(num_markets, 3)
        cols = st.columns(num_cols)

        for idx, (market_name, market_price) in enumerate(sorted_markets):
            col_idx = idx % num_cols
            with cols[col_idx]:
                # 최저가 여부에 따라 색상만 변경, 크기와 포맷은 동일
                is_cheapest = market_name == cheapest_name
                bg_color = (
                    "linear-gradient(135deg, #f0f9f4 0%, #e8f5e9 100%)"
                    if is_cheapest
                    else "#ffffff"
                )
                border_color = "#28a745" if is_cheapest else "#e0e0e0"
                border_width = "2px" if is_cheapest else "1px"
                price_color = "#28a745" if is_cheapest else "#333"
                shadow = (
                    "0 2px 4px rgba(40, 167, 69, 0.2)"
                    if is_cheapest
                    else "0 1px 3px rgba(0,0,0,0.1)"
                )

                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 15px; 
                                background: {bg_color}; border-radius: 8px; 
                                border: {border_width} solid {border_color}; margin-bottom: 10px;
                                box-shadow: {shadow}; min-height: 80px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="color: #666; font-size: 12px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase;">
                            {market_name}
                        </div>
                        <div style="color: {price_color}; font-size: 20px; font-weight: 700;">
                            {market_price:,.0f}원
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # 가격 차이 표시
        if num_markets > 1:
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 15px; padding-top: 15px; 
                            border-top: 2px dashed #e0e0e0;">
                    <div style="color: #666; font-size: 13px; margin-bottom: 5px;">
                        최고가와 최저가 차이
                    </div>
                    <div style="color: #4A90E2; font-size: 22px; font-weight: bold;">
                        {price_diff:,.0f}원
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


def render_eco_summary_stats(df_data: pd.DataFrame):
    """요약 통계를 렌더링합니다.

    Args:
        df_data: 데이터프레임
    """
    st.subheader("📈 요약 통계")
    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        total_records = len(df_data)
        st.metric("총 레코드 수", f"{total_records:,}개")

    with summary_col2:
        unique_items = (
            df_data["item_nm"].nunique() if "item_nm" in df_data.columns else 0
        )
        st.metric("고유 품목 수", f"{unique_items:,}개")

    with summary_col3:
        avg_price = df_data["avg_price"].mean() if "avg_price" in df_data.columns else 0
        st.metric("평균 가격", f"{avg_price:,.0f}원")


def render_price_comparison_pivot(df_data: pd.DataFrame):
    """마트별 가격 비교 피봇 테이블을 렌더링합니다.

    Args:
        df_data: 데이터프레임
    """

    try:
        # 피봇 테이블 생성: res_dt, item_cd, item_nm을 행으로, market_category를 열로, avg_price를 값으로
        df_pivot = df_data.pivot_table(
            index=["res_dt", "item_cd", "item_nm"],
            columns="market_category",
            values="avg_price",
            aggfunc="first",  # 중복이 있을 경우 첫 번째 값 사용
        ).reset_index()

        # 컬럼명 정리 (market_category가 컬럼명이 됨)
        df_pivot.columns.name = None

        # avg_price의 최대값과 최소값의 차이를 계산하는 컬럼 추가
        # market_category 컬럼들만 선택 (res_dt, item_cd, item_nm 제외)
        price_columns = [
            col
            for col in df_pivot.columns
            if col not in ["res_dt", "item_cd", "item_nm"]
        ]

        if price_columns:
            # 각 행별로 가격 컬럼들의 최대값과 최소값 계산 (NaN 제외)
            df_pivot["가격차이"] = df_pivot[price_columns].max(
                axis=1, skipna=True
            ) - df_pivot[price_columns].min(axis=1, skipna=True)

            # 가격차이 컬럼을 마지막에 배치하기 위해 컬럼 순서 재정렬
            other_columns = [col for col in df_pivot.columns if col != "가격차이"]
            df_pivot = df_pivot[[*other_columns, "가격차이"]]

        # 가격차이가 큰 상위 6개 품목 카드
        if "가격차이" in df_pivot.columns:
            st.subheader("📊 가격차이가 큰 상위 6개 품목")

            # 가격차이 기준으로 내림차순 정렬하고 상위 6개 선택
            top_6_items = df_pivot.nlargest(6, "가격차이")

            # 카드 데이터 준비
            card_data = []
            for _, row in top_6_items.iterrows():
                item_nm = row["item_nm"]
                price_diff = row["가격차이"]

                # market_category별 가격 데이터 추출
                price_data = {}
                for col in df_pivot.columns:
                    if col not in ["res_dt", "item_cd", "item_nm", "가격차이"]:
                        price_value = row[col]
                        if pd.notna(price_value):
                            price_data[col] = price_value

                if price_data:
                    card_data.append({
                        "item_nm": item_nm,
                        "price_data": price_data,
                        "price_diff": price_diff,
                    })

            # 2열로 카드 배치 (각 열에 3개씩)
            col1, col2 = st.columns(2)

            with col1:
                for i in range(0, len(card_data), 2):
                    render_market_price_card(
                        index=i,
                        item_nm=card_data[i]["item_nm"],
                        price_data=card_data[i]["price_data"],
                        price_diff=card_data[i]["price_diff"],
                        border_color="#4A90E2",
                    )

            with col2:
                for i in range(1, len(card_data), 2):
                    render_market_price_card(
                        index=i,
                        item_nm=card_data[i]["item_nm"],
                        price_data=card_data[i]["price_data"],
                        price_diff=card_data[i]["price_diff"],
                        border_color="#4A90E2",
                    )

        st.divider()
        # 원본 데이터도 탭으로 제공
        with st.expander("📋 원본 데이터 보기"):
            st.dataframe(df_pivot, use_container_width=True)

    except Exception as pivot_error:
        st.error(f"피봇 테이블 생성 중 오류: {str(pivot_error)}")
        st.info("원본 데이터를 표시합니다.")
        st.dataframe(df_data, use_container_width=True)


def render_eco_page(conn: DatabaseConnection):
    """친환경 페이지 전체를 렌더링합니다."""
    st.title("친환경 살펴보기")
    st.divider()

    try:
        # 최신 데이터 쿼리 가져오기
        latest_data_query = get_latest_price_statistics_query(conn=conn)

        with st.spinner("Athena에서 최신 데이터를 불러오는 중..."):
            try:
                # Athena 쿼리 실행
                df_data = conn.execute_query(latest_data_query)

                if len(df_data) > 0:
                    # 최신 데이터 날짜 표시
                    latest_date = (
                        df_data["res_dt"].iloc[0]
                        if "res_dt" in df_data.columns
                        else "N/A"
                    )
                    st.info(f"📅 최신 데이터 날짜: {latest_date}")

                    # 요약 통계
                    render_eco_summary_stats(df_data)

                    st.divider()

                    # 마트별 가격 비교 피봇 테이블
                    render_price_comparison_pivot(df_data)
                else:
                    st.info("조회된 데이터가 없습니다.")

            except Exception as e:
                st.error(f"데이터 조회 중 오류 발생: {str(e)}")
                st.info("💡 Athena 연결 설정을 확인하세요.")

    except Exception as e:
        st.error(f"Athena 연결 오류: {str(e)}")
        st.info("""
        **Athena 연결 설정 확인:**
        - AWS 자격 증명이 설정되어 있는지 확인
        - 환경 변수 설정 확인:
            - `AWS_ACCESS_KEY_ID`: AWS Access Key
            - `AWS_SECRET_ACCESS_KEY`: AWS Secret Key
            - `AWS_REGION`: 기본값 `ap-northeast-2`
            - `ATHENA_DATABASE`: 기본값 `team3_gold`
            - `ATHENA_WORKGROUP`: 기본값 `team3-wg`
        """)
