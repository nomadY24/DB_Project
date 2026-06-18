import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="A-HIT Dashboard", page_icon="🛡️", layout="wide")

# Supabase 연결 설정 (캐싱하여 속도 향상)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 데이터 불러오기 함수
@st.cache_data(ttl=60) # 1분마다 새로고침
def load_data():
    response = supabase.table("packages").select("*").execute()
    return pd.DataFrame(response.data)

# --- 메인 화면 시작 ---
st.title("🛡️ A-HIT: 환각 패키지 위협 관제 레이더")
st.markdown("LLM이 지어낸 가짜(Hallucination) 파이썬 패키지를 실시간으로 탐지하고 모니터링합니다.")

# 데이터 불러오기
df = load_data()

# 데이터가 없을 경우 처리
if df.empty:
    st.info("현재 발견된 환각 패키지가 없습니다. 수집기(collector.py)를 실행해 주세요.")
else:
    # 1. 최상단 요약 지표 (Metrics)
    st.subheader("📊 실시간 위협 요약")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="탐지된 환각 패키지 수", value=f"{len(df)} 개")
    with col2:
        avg_score = int(df['risk_score'].mean())
        st.metric(label="평균 위험 점수", value=f"{avg_score} 점")
    with col3:
        high_risk_count = len(df[df['risk_score'] >= 80])
        st.metric(label="고위험 패키지 (80점 이상)", value=f"{high_risk_count} 개", delta_color="inverse")

    st.divider()

    # 화면을 두 부분으로 나누기 (좌측: 차트, 우측: 테이블)
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.subheader("📈 위협 레이더 (위험 점수 순)")
        # Plotly를 사용한 인터랙티브 막대 그래프
        fig = px.bar(
            df.sort_values('risk_score', ascending=False), 
            x='package_name', 
            y='risk_score',
            color='risk_score',
            color_continuous_scale='Reds',
            labels={'package_name': '패키지명', 'risk_score': '위험 점수'}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("📋 전체 탐지 목록")
        # 데이터프레임 예쁘게 출력 ('created_at' 제거됨)
        st.dataframe(
            df[['package_name', 'risk_score', 'status', 'score_registry']],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # 3. 상세 분석 패널 (피드백 요구사항)
    st.subheader("🔍 가짜 패키지 상세 분석")
    st.markdown("각 패키지의 세부 정보와 검증 결과를 확인하세요.")
    
    # 패키지별로 접었다 펼칠 수 있는 Expander 생성
    for index, row in df.iterrows():
        with st.expander(f"📦 {row['package_name']} (위험도: {row['risk_score']}점)"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**상태:** " + ("🔴 검토 대기(PENDING)" if row['status'] == 'PENDING' else "🟢 처리 완료(RESOLVED)"))
                # 'created_at' 출력 부분 삭제됨
            with c2:
                st.markdown(f"**레지스트리 검증 점수:** {row['score_registry']}점")
                st.markdown("**검증 결과:** PyPI 저장소 검색 결과 `404 Not Found`. LLM이 생성한 환각(가짜) 패키지로 판명됨.")
            
            # (추후 기능) 관리자 액션 버튼
            st.button("차단 목록에 추가 (준비 중)", key=f"btn_{row.get('id', index)}", disabled=True)