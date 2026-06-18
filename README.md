# 🛡️ A-HIT (AI-based Hallucination Intelligence Tracker)

**A-HIT**는 거대 언어 모델(LLM)이 존재하지 않는 가짜 파이썬 패키지를 추천하는 현상(Hallucination)을 실시간으로 유도, 탐지하고 관리하는 **오픈소스 기반 보안 관제 대시보드**입니다.

## 🌟 프로젝트 개요

최근 개발자들이 AI(ChatGPT, Gemini 등)에게 코딩이나 패키지 추천을 의존하는 비율이 높아지면서, AI가 존재하지 않는 패키지를 그럴싸하게 추천하는 '환각(Hallucination) 패키지 위협'이 새로운 보안 취약점으로 대두되고 있습니다. 해커가 이 가짜 패키지 이름으로 악성 코드를 진짜 레지스트리에 등록하면, 개발자는 의심 없이 이를 설치하게 됩니다.

A-HIT는 이러한 위협을 선제적으로 방어하기 위해 다음과 같은 기능을 수행합니다:

1. **환각 유도 (Honeypot):** 최신 LLM(Gemini)에 교묘한 프롬프트를 주입하여 가짜 패키지 추천을 유도합니다.

2. **실시간 검증:** 추천받은 패키지가 실제 PyPI에 존재하는지 `404 Not Found` 검증을 수행합니다.

3. **위협 관제 (Dashboard):** 발견된 환각 패키지를 클라우드 DB에 적재하고, 직관적인 대시보드를 통해 위협 점수와 상세 정보를 제공합니다.

## 🛠️ 기술 스택 (Tech Stack)

* **Language:** Python 3.12
* **AI/LLM:** Google Gemini 2.5 Flash API (`google-genai`)
* **Frontend/Dashboard:** Streamlit, Plotly
* **Backend/Database:** Supabase (PostgreSQL)

## 🚀 주요 기능 (Features)

### 1. 지능형 환각 수집기 (`collector.py`)

* 구글 Gemini API를 활용하여 지속적으로 AI의 패키지 추천 데이터를 수집합니다.
* PyPI REST API를 호출하여 패키지의 실제 존재 여부를 교차 검증합니다.
* 존재하지 않는 패키지 발견 시, 해당 데이터를 Supabase 클라우드 데이터베이스에 자동 적재합니다.

### 2. 위협 관제 대시보드 (`app.py`)

* **실시간 요약 (Metrics):** 탐지된 전체 환각 패키지 수와 평균 위험 점수를 제공합니다.
* **위협 레이더 차트:** Plotly를 활용하여 패키지별 위험도를 막대그래프로 시각화합니다.
* **상세 분석 패널:** Streamlit Expander를 통해 각 가짜 패키지의 상태, 검증 결과(404 에러 로그 등)를 상세히 조회할 수 있습니다.

## ⚙️ 설치 및 실행 방법 (How to run)

### 1. 환경 설정

~~~bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # (Mac/Linux)
# venv\Scripts\activate  # (Windows)

# 필요 패키지 설치
pip install streamlit supabase requests google-genai pandas plotly
~~~

### 2. 환경 변수 설정

프로젝트 루트 경로에 `.streamlit/secrets.toml` 파일을 생성하고 아래 키를 입력합니다.

~~~toml
SUPABASE_URL = "당신의_Supabase_URL"
SUPABASE_KEY = "당신의_Supabase_API_KEY"
GEMINI_API_KEY = "당신의_Gemini_API_KEY"
~~~

### 3. 실행

~~~bash
# 1) 데이터 수집기 실행 (환각 패키지 탐지 및 DB 저장)
python collector.py

# 2) 대시보드 실행
streamlit run app.py
~~~