"""지역별 지도 시각화 컴포넌트"""

import folium
import branca.colormap as cm
from folium import Element
import pandas as pd
import copy
from typing import Optional
import streamlit as st
from streamlit_folium import st_folium
from data.queries.region_queries import get_region_stats_query
from data.connection import DatabaseConnection
import json
from pathlib import Path


def create_region_map(
    geojson_data: dict,
    region_data: pd.DataFrame,
    price_column: str = "평균가격",
    region_column: str = "country_nm",
    selected_item: Optional[str] = None,
) -> folium.Map:
    """지역별 가격 데이터를 지도에 표시합니다.

    Args:
        geojson_data: GeoJSON 데이터
        region_data: 지역별 가격 데이터 (country_nm, 평균가격 등 포함)
        price_column: 가격 컬럼명
        region_column: 지역명 컬럼명
        selected_item: 선택된 품목명 (선택사항)

    Returns:
        folium.Map: 지도 객체
    """
    m = folium.Map(
        location=[35.5, 129.5],
        zoom_start=7,
        min_zoom=7,
        max_zoom=8,
        tiles="Esri.WorldGrayCanvas",
    )

    # 데이터가 없으면 기본 지도만 반환
    if region_data.empty:
        return m

    # 1) 키 정규화: 문자열/공백 통일
    region_data = region_data.copy()
    region_data[region_column] = region_data[region_column].astype(str).str.strip()

    price_map = region_data.set_index(region_column).to_dict("index")

    # 2) GeoJSON 딥카피 후 주입
    geojson_enriched = copy.deepcopy(geojson_data)

    # 3) 색상 스케일
    vmin = region_data[price_column].min()
    vmax = region_data[price_column].max()
    colormap = cm.LinearColormap(
        colors=["#2c7bb6", "#abd9e9", "#fdae61", "#d7191c"],  # Blue→Red
        vmin=vmin,
        vmax=vmax,
    )

    # 범례 추가
    item_display = selected_item if selected_item else "가격"
    legend = Element(f"""
    <div style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: rgba(255,255,255,0.9);
        padding: 10px 14px;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        font-size: 12px;
    ">

        <!-- 제목 -->
        <div style="
            text-align:right;
            margin-bottom:6px;
            color: #000;
        ">
            <b>{item_display}</br>가격 (원)</b>
        </div>

        <!-- 범례 본체 -->
        <div style="position: relative; height: 160px;">

            <!-- max 값 (왼쪽) -->
            <div style="
                position: absolute;
                top: -2px;
                right: 26px;
                white-space: nowrap;
                color: #d7191c;
            ">
                {vmax:,.0f}
            </div>

            <!-- min 값 (왼쪽) -->
            <div style="
                position: absolute;
                bottom: -2px;
                right: 26px;
                white-space: nowrap;
                color: #2c7bb6;
            ">
                {vmin:,.0f}
            </div>

            <!-- 컬러바 -->
            <div style="
                position: absolute;
                right: 0;
                width: 18px;
                height: 160px;
                background: linear-gradient(
                    to top,
                    #2c7bb6,
                    #abd9e9,
                    #fdae61,
                    #d7191c
                );
            "></div>

        </div>
    </div>
    """)

    m.get_root().html.add_child(legend)

    def style_function(feature):
        props = feature.get("properties", {})
        region = str(props.get("CITY_AB_NM", "")).strip()
        if region in price_map:
            price = price_map[region][price_column]
            return {
                "fillColor": colormap(price),
                "color": "#ECBA82",
                "weight": 1.2,
                "fillOpacity": 0.8,
            }
        return {
            "fillColor": "#eeeeee",
            "color": "#cccccc",
            "weight": 0.5,
            "fillOpacity": 0.3,
        }

    for feat in geojson_enriched["features"]:
        props = feat["properties"]
        region = str(props.get("CITY_AB_NM", "")).strip()

        if region in price_map:
            # 값 주입
            price_val = price_map[region][price_column]
            props["price"] = price_val

            # 안전한 포맷팅 처리
            price_str = (
                f"{int(price_val):,}원"
                if price_val is not None and not pd.isna(price_val)
                else "데이터 없음"
            )
            item_str = f"{selected_item}<br>" if selected_item else ""

            tooltip_html = f"""
            <b>{region}</b><br>
            {item_str}가격: {price_str}
            """

            folium.GeoJson(
                feat,
                style_function=style_function,
                tooltip=folium.Tooltip(tooltip_html, sticky=False),
            ).add_to(m)
        else:
            # 데이터 없는 지역은 기본 스타일로 추가
            folium.GeoJson(
                feat,
                style_function=style_function,
            ).add_to(m)

    return m


def render_region_map(
    geojson_data: dict,
    region_data: pd.DataFrame,
    price_column: str = "평균가격",
    region_column: str = "지역",
    selected_item: Optional[str] = None,
    height: int = 500,
):
    """Streamlit에서 지역별 지도를 렌더링합니다.

    Args:
        geojson_data: GeoJSON 데이터
        region_data: 지역별 가격 데이터
        price_column: 가격 컬럼명
        region_column: 지역명 컬럼명
        selected_item: 선택된 품목명
        height: 지도 높이 (픽셀)
    """
    if region_data.empty:
        st.info("지도에 표시할 데이터가 없습니다.")
        return

    # 지도 생성
    m = create_region_map(
        geojson_data, region_data, price_column, region_column, selected_item
    )

    # Streamlit에 지도 표시
    st_folium(m, width=700, height=height, returned_objects=[])


def render_selected_item_region_map(
    conn: DatabaseConnection, date_filter=None, category_filter=None
):
    """선택된 품목의 지역별 지도를 표시하는 함수.

    Args:
        date_filter: 날짜 필터
        category_filter: 카테고리 필터
    """
    if not (
        st.session_state.get("show_region_map", False)
        and "selected_item_nm" in st.session_state
        and "selected_kind_nm" in st.session_state
    ):
        return

    st.divider()
    st.subheader(
        f"🗺️ {st.session_state.selected_item_nm}({st.session_state.selected_kind_nm}) 지역별 가격 지도"
    )

    # GeoJSON 로드
    @st.cache_resource
    def load_geojson():
        path = Path("assets/retail_regions.json")
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    merged_geojson = load_geojson()

    # 지역별 데이터 조회
    region_stats_query = get_region_stats_query(
        date_filter=date_filter, category_filter=category_filter, conn=conn
    )

    with st.spinner("지역별 데이터를 불러오는 중..."):
        try:
            df_region = conn.execute_query(region_stats_query)

            if len(df_region) > 0:
                # 선택된 품목 필터링
                df_filtered = df_region[
                    (df_region["품목"] == st.session_state.selected_item_nm)
                    & (df_region["품종"] == st.session_state.selected_kind_nm)
                ]

                if len(df_filtered) > 0:
                    # 지역별 평균 가격으로 그룹화
                    df_region_agg = (
                        df_filtered.groupby("지역")
                        .agg({"평균가격": "mean"})
                        .reset_index()
                    )

                    col1, col2 = st.columns(2)

                    # 지도 표시
                    with col1:
                        render_region_map(
                            merged_geojson,
                            df_region_agg,
                            price_column="평균가격",
                            region_column="지역",
                            selected_item=f"{st.session_state.selected_item_nm}({st.session_state.selected_kind_nm})",
                            height=650,
                        )

                    # 데이터 테이블도 함께 표시
                    with col2:
                        st.dataframe(
                            df_filtered[["지역", "평균가격", "최저가격", "최고가격"]],
                            use_container_width=True,
                        )

                    # 닫기 버튼
                    if st.button("지도 닫기", key="close_map_btn"):
                        st.session_state.show_region_map = False
                        st.session_state.selected_item_nm = None
                        st.session_state.selected_kind_nm = None
                        st.rerun()
                else:
                    st.info(
                        f"{st.session_state.selected_item_nm}({st.session_state.selected_kind_nm})에 대한 지역별 데이터가 없습니다."
                    )
                    if st.button("지도 닫기", key="close_map_btn_no_data"):
                        st.session_state.show_region_map = False
                        st.session_state.selected_item_nm = None
                        st.session_state.selected_kind_nm = None
                        st.rerun()
            else:
                st.info("지역별 데이터가 없습니다.")
        except Exception as e:
            st.error(f"지역별 데이터 조회 중 오류: {str(e)}")
