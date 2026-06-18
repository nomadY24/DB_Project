import requests
import tomllib
from supabase import create_client, Client

# 1. Supabase 연결 설정 (.streamlit/secrets.toml 파일 읽어오기)
# Streamlit 웹이 아닌 일반 백엔드 스크립트이므로 파일을 직접 읽어옵니다.
def get_supabase_client() -> Client:
    try:
        with open(".streamlit/secrets.toml", "rb") as f:
            secrets = tomllib.load(f)
        url = secrets["SUPABASE_URL"]
        key = secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except FileNotFoundError:
        print("🚨 에러: .streamlit/secrets.toml 파일을 찾을 수 없습니다.")
        exit(1)

supabase = get_supabase_client()

# 2. LLM 응답 시뮬레이션 (JSON 강제 프롬프트의 결과물을 흉내냅니다)
# (나중에 이 부분을 실제 OpenAI API 연동 코드로 교체할 예정입니다)
def simulate_llm_response():
    print("🤖 LLM에게 파이썬 데이터 분석 패키지 추천을 요청합니다...")
    # LLM이 진짜 패키지와 가짜(환각) 패키지를 섞어서 대답했다고 가정합니다.
    return [
        {"package_name": "pandas", "reason": "데이터 조작에 필수적입니다."},
        {"package_name": "numpy", "reason": "수치 계산에 좋습니다."},
        {"package_name": "pandas-ai-optimizer-v2", "reason": "AI 기반 데이터 자동 최적화 기능"},
        {"package_name": "fastapi-secure-jwt-auth-lib", "reason": "강력한 JWT 인증 구현"}
    ]

# 3. PyPI 레지스트리 404 검증 로직
def check_pypi_exists(package_name: str) -> bool:
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    
    # 404 에러가 나면 존재하지 않는 패키지 (환각)
    if response.status_code == 404:
        return False
    return True

# 4. 메인 수집 루프
def run_collector():
    print("🚀 A-HIT 데이터 수집기를 시작합니다...\n")
    packages = simulate_llm_response()

    for pkg in packages:
        name = pkg["package_name"]
        print(f"🔍 검증 중: '{name}' ...", end=" ")

        is_real = check_pypi_exists(name)

        if is_real:
            print("✅ [정상] PyPI에 존재하는 패키지입니다.")
        else:
            print("🚨 [경고] 404 Not Found - 환각 패키지 발견!")

            # 위험 점수 계산 (수집기 초기값)
            risk_score = 80
            score_registry = 40 # 레지스트리 부재로 인한 치명적 점수 부여

            # DB에 삽입할 데이터 세팅
            data = {
                "package_name": name,
                "risk_score": risk_score,
                "status": "PENDING",
                "score_registry": score_registry
            }

            try:
                # DB의 packages 테이블에 삽입
                supabase.table("packages").insert(data).execute()
                print(f"   💾 DB 저장 완료: 대시보드에 '{name}'이(가) 추가되었습니다!\n")
            except Exception as e:
                # 패키지 이름이 중복(UNIQUE 제약조건)되면 에러가 날 수 있습니다.
                print(f"   ⚠️ DB 저장 실패 (이미 수집된 패키지일 수 있습니다): {e}\n")

if __name__ == "__main__":
    run_collector()