import streamlit as st
import requests

# ============================================
# 🔑 네이버 API 인증 정보 (사이드바 입력 방식)
# ============================================
st.set_page_config(page_title="네이버 뉴스 검색기", page_icon="📰")

with st.sidebar:
    st.header("🔑 API 설정")
    client_id = st.text_input("Naver Client ID", type="password")
    client_secret = st.text_input("Naver Client Secret", type="password")
    st.info("네이버 개발자 센터에서 발급받은 키를 입력하세요.")

# ------------------------------------------------
# 1️⃣ 뉴스 제목 정제 함수
# ------------------------------------------------
def clean_title(title):
    title = title.replace("<b>", "").replace("</b>", "").replace("&quot;", '"').replace("&amp;", "&")
    return title

# ------------------------------------------------
# 2️⃣ 메인 UI 및 로직
# ------------------------------------------------
st.title("📰 네이버 뉴스 실시간 검색기")
st.markdown("검색어를 입력하면 관련 뉴스를 최대 10개까지 가져옵니다.")

keyword = st.text_input("🔍 검색어를 입력하세요", placeholder="예: 인공지능, 테슬라, 맛집")
search_button = st.button("뉴스 검색하기")

if search_button:
    if not client_id or not client_secret:
        st.error("⚠️ 사이드바에 Client ID와 Secret을 입력해주세요!")
    elif not keyword:
        st.warning("🔍 검색어를 입력해주세요.")
    else:
        # API 호출 설정
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        params = {
            "query": keyword,
            "display": 10,
            "sort": "sim"
        }

        with st.spinner('뉴스를 불러오는 중...'):
            response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])

            if items:
                st.success(f"'{keyword}'에 대한 검색 결과입니다.")
                for i, item in enumerate(items, 1):
                    title = clean_title(item.get("title", ""))
                    link = item.get("link", "")
                    pub_date = item.get("pubDate", "")
                    description = clean_title(item.get("description", ""))

                    # 뉴스 카드 형태 출력
                    with st.expander(f"{i}. {title}"):
                        st.write(f"📅 **발행일:** {pub_date}")
                        st.write(f"📝 **요약:** {description}")
                        st.markdown(f"[🔗 기사 원문 보기]({link})")
            else:
                st.info("검색 결과가 없습니다.")
        
        elif response.status_code == 401:
            st.error("❌ 인증 오류: API 키를 다시 확인해주세요.")
        elif response.status_code == 429:
            st.error("❌ 한도 초과: API 호출 한도를 초과했습니다.")
        else:
            st.error(f"❌ 오류 발생: {response.status_code}")

# 하단 안내
st.divider()
st.caption("Powered by Naver Search API & Streamlit")