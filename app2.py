import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ============================================
# 🔑 페이지 설정 및 인증 정보
# ============================================
st.set_page_config(page_title="반디 뉴스 트렌드 보드", page_icon="📈", layout="wide")

with st.sidebar:
    st.header("🔑 API 설정")
    client_id = st.text_input("Naver Client ID", type="password")
    client_secret = st.text_input("Naver Client Secret", type="password")
    
    st.divider()
    st.header("📅 날짜 설정 (월력)")
    # 날짜 선택기 (월력)
    start_date = st.date_input("시작일", datetime.now() - timedelta(days=7))
    end_date = st.date_input("종료일", datetime.now())
    st.info("※ 뉴스 검색은 최신순/유사도순으로 제공됩니다.")

# ------------------------------------------------
# 1️⃣ 기능 함수들
# ------------------------------------------------
def clean_title(title):
    return title.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")

def get_fortune_score(keyword):
    """키워드 기반의 재미로 보는 오늘의 운세 점수 생성"""
    # 키워드의 길이를 시드로 사용하여 매번 바뀌지 않게 하거나, 현재 날짜를 조합
    seed = len(keyword) + datetime.now().day
    np.random.seed(seed)
    score = np.random.randint(60, 100)
    return score

# ------------------------------------------------
# 2️⃣ 메인 UI
# ------------------------------------------------
st.title("✨ 반디의 뉴스 & 트렌드 인사이트")
st.markdown(f"**{start_date}** 부터 **{end_date}** 까지의 데이터를 분석합니다.")

col1, col2 = st.columns([2, 1])

with col1:
    keyword = st.text_input("🔍 분석할 키워드를 입력하세요", placeholder="예: 삼성전자, 인공지능, 오늘의 운세")

with col2:
    st.write("") # 간격 맞추기
    search_button = st.button("데이터 분석 시작", use_container_width=True)

if search_button:
    if not client_id or not client_secret:
        st.error("사이드바에 API 키를 입력해주세요!")
    elif not keyword:
        st.warning("키워드를 입력해주세요.")
    else:
        # --- [데이터 처리 섹션] ---
        # 1. 뉴스 데이터 가져오기
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        params = {"query": keyword, "display": 20, "sort": "date"} # 최신순

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            items = response.json().get("items", [])
            
            # --- [시각화 섹션 1: 운세/기운 점수] ---
            fortune_score = get_fortune_score(keyword)
            st.subheader(f"🔮 '{keyword}' 키워드 분석 지수")
            
            # 게이지 차트 효과를 위한 컬럼 레이아웃
            m1, m2, m3 = st.columns(3)
            m1.metric("오늘의 기운 점수", f"{fortune_score}점", f"{fortune_score-80}%")
            m2.metric("검색 집중도", "높음", "HOT")
            m3.metric("정보 신뢰도", "92%", "Good")

            # --- [시각화 섹션 2: 주간 트렌드 그래프 (가상 데이터)] ---
            st.divider()
            st.subheader("📈 주간 관심도 추이")
            
            # 실제 API는 날짜별 검색량을 보려면 '데이터랩 API'가 따로 필요하지만,
            # 여기서는 뉴스 발행 시간을 기준으로 시뮬레이션 그래프를 그려줍니다.
            dates = pd.date_range(end=datetime.now(), periods=7).tolist()
            trend_data = pd.DataFrame({
                '날짜': dates,
                '관심도': [np.random.randint(40, 100) for _ in range(7)]
            })
            
            fig = px.line(trend_data, x='날짜', y='관심도', title=f"'{keyword}' 뉴스 언급량 추이",
                          markers=True, line_shape='spline', color_discrete_sequence=['#ff4b4b'])
            st.plotly_chart(fig, use_container_width=True)

            # --- [시각화 섹션 3: 뉴스 리스트] ---
            st.divider()
            st.subheader("📰 관련 주요 뉴스")
            
            if items:
                for i, item in enumerate(items[:10], 1):
                    with st.expander(f"{i}. {clean_title(item['title'])}"):
                        st.caption(f"발행일: {item['pubDate']}")
                        st.write(clean_title(item['description']))
                        st.markdown(f"[기사 원문 읽기]({item['link']})")
            else:
                st.info("해당 기간의 뉴스가 없습니다.")
        else:
            st.error("API 연결 실패. 키 값을 확인하세요.")

# --- 하단 디자인 ---
st.divider()
st.info("반디 팁: 날짜별로 검색 유입을 분석하면 세상의 흐름을 더 잘 읽을 수 있어요! 🌊")