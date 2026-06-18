import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 페이지 기본 설정
st.set_page_config(
    page_title="A-HIT Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# [기능 1] Supabase DB 연결 및 초기화
# ==========================================
@st.cache_resource
def init_connection() -> Client:
    try:
        # .streamlit/secrets.toml 에서 URL과 KEY를 불러옵니다.
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"데이터베이스 연결 중 오류가 발생했습니다: {e}")
        st.stop()  # 연결 실패 시 앱 실행을 중지합니다.

supabase = init_connection()

# ==========================================
# [기능 2] 화면 라우팅 (Sidebar Navigation)
# ==========================================
st.sidebar.title("🛡️ A-HIT")
st.sidebar.caption("AI-Hallucination Intelligence Tracker")
st.sidebar.write("---")

menu = st.sidebar.selectbox(
    "메뉴 이동",
    ["위협 대시보드", "데이터 수집 로그", "방어 정책 관리"]
)

# ==========================================
# 메인 화면 구성
# ==========================================
if menu == "위협 대시보드":
    st.title("🚨 실시간 감지된 가짜 패키지 현황")
    
    # [기능 3] 실시간 감지 패키지 현황 (메인 데이터 그리드)
    try:
        # status가 'FALSE_POSITIVE'가 아닌 데이터를 risk_score 내림차순으로 10개 조회
        response = supabase.table("packages") \
            .select("*") \
            .neq("status", "FALSE_POSITIVE") \
            .order("risk_score", desc=True) \
            .limit(10) \
            .execute()
        
        data = response.data
    except Exception as e:
        st.error(f"데이터 조회 중 오류가 발생했습니다: {e}")
        data = []

    # 데이터가 없을 경우의 예외 처리
    if not data:
        st.warning("현재 데이터베이스에 탐지된 위협 정보가 없습니다.")
    else:
        # 데이터를 Pandas DataFrame으로 변환
        df = pd.DataFrame(data)
        
        # 노출할 주요 컬럼 정의 및 필터링
        display_columns = [
            'package_name', 'risk_score', 'status', 
            'occurrence_count', 'last_detected_at'
        ]
        
        # DataFrame 화면 표출
        st.dataframe(df[display_columns], use_container_width=True)
        
        st.write("---")
        
        # [기능 4] 상세 분석 패널 (가짜 패키지 상세 분석)
        st.subheader("🔍 가짜 패키지 상세 분석")
        
        # DB 재조회 없이 기존 데이터프레임의 package_name 목록을 selectbox에 사용
        selected_package_name = st.selectbox(
            "상세 정보를 확인할 패키지를 선택하세요:",
            df['package_name'].tolist()
        )
        
        if selected_package_name:
            # 선택된 패키지 정보만 DataFrame에서 필터링
            package_info = df[df['package_name'] == selected_package_name].iloc[0]
            
            # 요약 정보 마크다운 구성
            info_text = f"""
            ### 패키지명: `{package_info.get('package_name', 'N/A')}`
            
            - **최종 위험 지수:** 🚨 **{package_info.get('risk_score', 0)} 점**
            - **레지스트리 미존재 점수:** {package_info.get('score_registry', 0)} 점
            - **이름 유사도 점수:** {package_info.get('score_similarity', 0)} 점
            - **상태:** {package_info.get('status', 'PENDING')}
            """
            
            # st.info 형태로 요약 카드 표시
            st.info(info_text)

# 미구현 페이지 처리 로직
elif menu == "데이터 수집 로그":
    st.title("📊 데이터 수집 로그")
    st.info("현재 개발 중입니다.")

elif menu == "방어 정책 관리":
    st.title("🛡️ 방어 정책 관리")
    st.info("현재 개발 중입니다.")