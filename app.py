import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

from components.channel_cards import render_channel_comparison_sections
from components.extra_panel import render_extra_panel
from components.price_cards import render_price_drop_cards, render_price_rise_cards
from components.region_map import render_selected_item_region_map
from components.season_selector import render_season_selector
from components.eco_panel import render_eco_page
from data.queries.channel_queries import get_channel_comparison_query
from data.queries.price_queries import (
    get_country_list,
    get_price_drop_top3_query,
    get_price_rise_top3_query,
)
from data.connection import get_database_connection


def load_css():
    base_path = Path(__file__).parent
    with open(base_path / "styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# sample_data 삭제 후 임시 데이터
summary = {
    "cheap": {"item_nm": "연결 테스트", "avg_price": 0},
    "expensive": {"item_nm": "연결 테스트", "avg_price": 0},
    "suggest": {"item_nm": "연결 테스트", "avg_price": 0},
}

popular_items = []

st.set_page_config(page_title="농산물 가격 대시보드", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "main"

conn = get_database_connection(
    "athena"
)  # 여기서 rds와 athena 중 하나를 선택할 수 있도록 해야함

# 세션 상태 초기화
if "show_region_map" not in st.session_state:
    st.session_state.show_region_map = False
if "selected_item_nm" not in st.session_state:
    st.session_state.selected_item_nm = None
if "selected_kind_nm" not in st.session_state:
    st.session_state.selected_kind_nm = None

# -------------------------
# 사이드바 (좌측 탭)
# -------------------------
with st.sidebar:
    st.title("메뉴")

    if st.button("🧺 오늘의 식재료", use_container_width=True):
        st.session_state.page = "main"

    if st.button("🌱 친환경 정보", use_container_width=True):
        st.session_state.page = "eco"

    if st.button("🏪 유통업체별 정보", use_container_width=True):
        st.session_state.page = "dist"

    st.divider()

    st.caption("필터 영역 (추후 추가)")

# -------------------------
# 메인 콘텐츠
# -------------------------
if st.session_state.page == "main":
    st.title("오늘 눈여겨볼 만한 식재료들")
    st.divider()

    # -------------------------
    # 1️⃣ 상단 필터 (columns 밖)
    # -------------------------
    country_list_df = conn.execute_query(get_country_list(conn=conn))
    country_list = (
        country_list_df["country_nm"].drop_duplicates().sort_values().tolist()
    )

    if "country" not in st.session_state:
        st.session_state.country = country_list[0]  # 기본값

    country = st.selectbox(
        "지역 선택",
        country_list,
        index=country_list.index(st.session_state.country),
        key="country",
    )

    center, right = st.columns([3, 1])

    # -------------------------
    # 중앙 영역
    # -------------------------

    with center:
        c1, c2 = st.columns(2)
        # tab1, tab2 = st.tabs(["가격 하락 TOP3", "가격 상승 TOP3"])

        with c1:
            # with tab1:
            st.subheader("📉 전일 대비 가격 하락 TOP 3")

            query = get_price_drop_top3_query(country_filter=country, conn=conn)
            print(query)
            cheep_df = conn.execute_query(query)

            render_price_drop_cards(cheep_df)

        with c2:
            # with tab2:
            st.subheader("📈 전일 대비 가격 상승 TOP 3")

            query = get_price_rise_top3_query(
                country_filter=country, conn=conn
            )  # , limit=3)
            rise_df = conn.execute_query(query)

            render_price_rise_cards(rise_df)

        # with c3:
        #     st.subheader("이건 어때요")
        #     price_card(summary["suggest"], '#eaf7ea')

        st.divider()

        bottom_left, bottom_right = st.columns([1, 2])

        with bottom_left:
            render_season_selector()

        with bottom_right:
            st.subheader("🌱 제철 식재료 지역별 가격 지도")
            st.caption("※ 현재 제철 식재료 기준")

    # -------------------------
    # 우측 영역 (추가 기능)
    # -------------------------
    with right:
        render_extra_panel()


# =================================================
# 친환경 페이지
# =================================================
elif st.session_state.page == "eco":
    render_eco_page(conn)

# =================================================
# 유통업체 페이지
# =================================================
elif st.session_state.page == "dist":
    st.title("일반 농수산물 살펴보기")
    st.divider()

    try:
        # 날짜 필터 추가
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            date_filter = st.date_input("날짜 선택", value=None, key="dist_date")
        with col2:
            category_filter = st.selectbox(
                "카테고리 선택",
                [
                    "전체",
                    "식량작물",
                    "채소류",
                    "특용작물",
                    "과일류",
                    "축산물",
                    "수산물",
                ],
                key="dist_category",
            )
        with col3:
            # 버튼을 아래로 정렬하기 위한 빈 공간 추가
            st.markdown("<br>", unsafe_allow_html=True)
            query_button = st.button(
                "데이터 조회",
                type="primary",
                key="dist_query_button",
                use_container_width=True,
            )

        # 유통 vs 전통 비교 쿼리 생성
        comparison_query = get_channel_comparison_query(
            date_filter=date_filter,
            category_filter=category_filter,
            limit=None,
            conn=conn,
        )

        if query_button:
            with st.spinner("데이터를 불러오는 중..."):
                try:
                    df_comparison = conn.execute_query(comparison_query)

                    if len(df_comparison) > 0:
                        # 세션 상태에 쿼리 결과 저장
                        st.session_state.df_comparison = df_comparison
                        st.session_state.query_date_filter = date_filter
                        st.session_state.query_category_filter = category_filter

                        # 요약 통계
                        st.subheader("📈 요약 통계")
                        summary_col1, summary_col2, summary_col3 = st.columns(3)

                        with summary_col1:
                            avg_yutong = df_comparison["유통_평균가격"].mean()
                            st.metric("유통 평균 가격", f"{avg_yutong:,.0f}원")

                        with summary_col2:
                            avg_jeontong = df_comparison["전통_평균가격"].mean()
                            st.metric("전통 평균 가격", f"{avg_jeontong:,.0f}원")

                        with summary_col3:
                            avg_diff = df_comparison["가격차이"].mean()
                            st.metric("평균 가격 차이", f"{avg_diff:,.0f}원")

                        st.divider()

                        render_channel_comparison_sections(df_comparison)

                        # 선택된 품목이 있으면 지역별 지도 표시
                        render_selected_item_region_map(
                            conn=conn,
                            date_filter=st.session_state.get("query_date_filter"),
                            category_filter=st.session_state.get(
                                "query_category_filter"
                            ),
                        )

                        st.divider()
                        st.subheader("📊 유통 vs 전통 가격 비교")
                        st.dataframe(df_comparison, use_container_width=True)
                    else:
                        st.info("조회된 데이터가 없습니다.")

                except Exception as e:
                    st.error(f"데이터 조회 중 오류 발생: {str(e)}")
                    st.info("💡 Athena 연결 설정을 확인하세요.")

        # 쿼리 버튼이 눌러지지 않았지만 이전에 조회한 데이터가 있고 지도 표시 요청이 있는 경우
        elif (
            "df_comparison" in st.session_state
            and len(st.session_state.df_comparison) > 0
        ):
            df_comparison = st.session_state.df_comparison

            # 요약 통계
            st.subheader("📈 요약 통계")
            summary_col1, summary_col2, summary_col3 = st.columns(3)

            with summary_col1:
                avg_yutong = df_comparison["유통_평균가격"].mean()
                st.metric("유통 평균 가격", f"{avg_yutong:,.0f}원")

            with summary_col2:
                avg_jeontong = df_comparison["전통_평균가격"].mean()
                st.metric("전통 평균 가격", f"{avg_jeontong:,.0f}원")

            with summary_col3:
                avg_diff = df_comparison["가격차이"].mean()
                st.metric("평균 가격 차이", f"{avg_diff:,.0f}원")

            st.divider()

            render_channel_comparison_sections(df_comparison)

            # 선택된 품목이 있으면 지역별 지도 표시
            render_selected_item_region_map(
                conn=conn,
                date_filter=st.session_state.get("query_date_filter"),
                category_filter=st.session_state.get("query_category_filter"),
            )

            st.divider()
            st.subheader("📊 유통 vs 전통 가격 비교")
            st.dataframe(df_comparison, use_container_width=True)

    except Exception as e:
        st.error(f"연결 오류: {str(e)}")
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

# 사이드바 하단에 연결 정보 표시
with st.sidebar:
    st.markdown("---")
    st.markdown("### 연결 정보")

    # 현재 페이지에 따라 다른 연결 정보 표시
    st.info(f"""
    **{conn.__class__.__name__} 설정:**
    - Database: {conn.get_config()[0]}
    - WorkGroup: {conn.get_config()[1]}
    """)
    # RDS 헬스체크
    try:
        conn.execute_query("SELECT 1 FROM mart.api10_price_comparison LIMIT 1")
        st.success("RDS 연결 정상")
    except Exception:
        st.error("RDS 연결 실패")
