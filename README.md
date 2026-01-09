# 🌾 Threelacha Streamlit Dashboard (EC2)

본 레포지토리는 농축수산물 가격 데이터를 시각화·탐색하기 위한 **Streamlit 기반 대시보드 서비스**를 관리·운영하기 위한 레포지토리입니다.<br>
Airflow + dbt 파이프라인을 통해 적재·가공된 데이터를 기반으로, 지역별·유통채널별 가격 동향을 한눈에 확인할 수 있는 사용자 인터페이스를 제공합니다.

> ⚠️ 본 레포는 데이터 수집·변환 파이프라인을 포함하지 않으며, 이미 구축된 데이터 저장소를 조회(Read-only) 하는 프레젠테이션 레이어입니다.
---

## 🎥 대시보드 미리보기
### 🧺 오늘의 식재료
![오늘의 식재료](assets/demo/demo1.gif)

### 🌱 친환경 정보
![친환경 농수산물](assets/demo/demo2.gif)

### 🏪  유통업체별 가격 비교
![유통업체별 비교](assets/demo/demo3.gif)

---

## ✨ 주요 특징

- Streamlit 기반 운영용 대시보드
- Airflow-dbt 파이프라인 결과를 실시간 반영
- 지도(Folium) + 차트(Altair) 기반 시각화
- EC2 단일 인스턴스 상 실행 환경
- GitHub Actions 기반 자동 배포

---

## 🧩 페이지 구성
### 오늘의 식재료
- 전일 대비 가격 상승/하락 TOP3
- 지역별 가격 분포 지도
- 제철 식자재 가격 비교
### 친환경 정보
- 친환경 품목 수
- 유통 채널별 가격 비교
### 유통업체 비교
- 유통 vs 전통시장 가격
- 평균 가격 차이 분석

---

## 🚀 실행 방법
### 1️⃣ 레포 클론
```
git clone git@github.com:dev7-team3/Threelacha_streamlit.git
cd Threelacha_streamlit
```
### 2️⃣ Docker 실행
```
docker run -d \
     --name threelacha-streamlit \
     --restart unless-stopped \
     -p 8501:8501 \
     --env-file /home/ubuntu/Threelacha_streamlit/.env \
     threelacha-streamlit:latest
``` 

---

## 📁 디렉토리 구조

```
THREELACHA_STREAMLIT/
├── .github/
│   └── workflows/
│       └── deploy.yml              # EC2 Streamlit 자동 배포 파이프라인
│
├── assets/
│   ├── demo/                       # README용 시연 GIF
│   ├── fonts/                      # 커스텀 한글 폰트
│   ├── korea_sido.json             # 행정구역 GeoJSON
│   └── retail_regions.json         # 유통 권역 GeoJSON
│
├── components/                     # UI 컴포넌트 모듈
│   ├── channel_cards.py            # 유통 채널 비교 카드
│   ├── eco_panel.py                # 친환경 정보 페이지
│   ├── extra_panel.py              # 보조 패널
│   ├── price_cards.py              # 가격 상승/하락 카드
│   ├── price_graph.py              # 도넛/그래프 시각화
│   ├── region_map.py               # 지역별 지도 시각화
│   ├── season_cards.py             # 제철 가격 카드
│   ├── season_map.py               # 제철 가격 지도
│   └── season_selector.py          # 제철 선택 UI
│
├── data/
│   ├── queries/                    # SQL Query 모듈
│   │   ├── channel_queries.py
│   │   ├── eco_channel_queries.py
│   │   ├── meta_queries.py
│   │   ├── price_queries.py
│   │   ├── region_queries.py
│   │   ├── season_queries.py
│   │   └── query_utils.py
│   ├── athena_connection.py        # Athena 연결
│   ├── rds_connection.py           # RDS 연결
│   ├── connection.py               # 커넥션 추상화
│   └── logger.py                   # 공통 로깅
│
├── app.py                          # Streamlit 메인 엔트리포인트
├── styles.css                      # UI 스타일 정의
├── Dockerfile                      # Streamlit 운영 이미지
├── pyproject.toml                  # Python 의존성 정의
├── uv.lock                         # 의존성 고정 파일
├── UV_SETUP.md                     # uv 환경 설정 가이드
├── season_df_debug.csv             # 디버깅용 데이터
├── .gitignore
├── .dockerignore
└── README.md
```

---

## ⚙️ Runtime Environment

- Python: 3.11
- Framework: Streamlit
- Visualization: Altair, Folium
- DB: Amazon RDS
- Font: 커스텀 한글 폰트(Base64 embedding)
- Dependency Management: uv

---

## 🔐 Environment Variables

운영 환경에서는 EC2 인스턴스 내 .env 파일을 사용합니다.
```
# 데이터 소스 선택
DB_CONNECTION=athena   # or rds

# AWS (Athena 사용 시)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=

# RDS
RDS_HOST=
RDS_PORT=
RDS_DB=
RDS_USER=
RDS_PASSWORD=
```
> ⚠️ 본 레포는 데이터 적재 및 변환을 수행하지 않으며,  
> Airflow + dbt 레포에서 데이터가 사전에 준비되어 있어야 정상 동작합니다.

---

## 🌐 운영 환경 배포 (EC2)

- GitHub Actions (.github/workflows/deploy.yml) 기반
- main 브랜치 merge 시 자동 배포
- 기존 프로세스 종료 후 재기동
- 포트: 8501

---

## 📎 Notes

- Airflow / dbt 파이프라인이 선행되어야 정상 동작합니다.
- 지도 데이터(assets/*.json)는 행정구역 기준으로 관리됩니다.
- 스타일 및 폰트 변경은 styles.css 및 load_css()에서 관리합니다.

---

## 👥 Maintainers

Threelacha Data Engineering Team

[구다혜](https://github.com/dahye83) [김지연](https://github.com/Jiyeon0027)  [박정은](https://github.com/jjung121) [정수진](https://github.com/jipipes) 

---
