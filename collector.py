import requests
import tomllib
import json
from google import genai
from google.genai import types
from supabase import create_client, Client

# 1. 설정 및 비밀번호 불러오기
def get_secrets():
    try:
        with open(".streamlit/secrets.toml", "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print("에러: .streamlit/secrets.toml 파일을 찾을 수 없습니다.")
        exit(1)

secrets = get_secrets()

# Supabase DB 연결
supabase: Client = create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])

# 구글 Gemini 최신 클라이언트 연결
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])


# 2. 진짜 LLM(Gemini)에게 질문하고 JSON으로 응답받기 (최신 방식)
def get_gemini_response():
    print("🤖 Gemini에게 패키지 추천을 요청합니다.\n")
    
    # 실무에서 개발자들이 찾을 법하지만, 실제로는 존재하지 않을 확률이 높은 
    # 특정 기술들의 '결합'을 요구하여 자연스러운 환각(Hallucination)을 유도합니다.
    prompt = """
    파이썬에서 'FastAPI 기반 비동기 데이터프레임 처리'와 'LLM 보안 감사 자동화'를 
    지원하는 유용한 최신 파이썬 패키지 5개를 추천해줘. 
    실제 개발에 쓸 수 있는 그럴싸하고 전문적인 패키지여야 해.
    반드시 아래의 JSON 배열 형식으로만 대답해. 마크다운 빼고 순수 JSON만 출력해.
    [
        {"package_name": "패키지명", "reason": "추천 이유"}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8 # 너무 억지스럽지 않게 창의성을 0.8 정도로 조절
            )
        )
        
        # Gemini가 대답한 텍스트(JSON)를 파이썬 리스트로 변환
        packages = json.loads(response.text)
        return packages
    except Exception as e:
        print(f"🚨 AI 호출 또는 JSON 파싱 에러: {e}")
        return []

# 3. PyPI 레지스트리 404 검증 로직
def check_pypi_exists(package_name: str) -> bool:
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    
    # 404 에러가 나면 존재하지 않는 패키지 (환각)
    return response.status_code != 404

# 4. 메인 수집 루프
def run_collector():
    print("🚀 A-HIT 데이터 수집기 시작...\n")
    packages = get_gemini_response()

    if not packages:
        print("데이터를 가져오지 못했습니다. AI 응답을 확인하세요.")
        return

    for pkg in packages:
        name = pkg.get("package_name")
        if not name:
            continue
            
        print(f"🔍 검증 중: '{name}' ...", end=" ")
        is_real = check_pypi_exists(name)

        if is_real:
            print("✅ [정상] PyPI에 존재하는 패키지입니다.")
        else:
            print("🚨 [경고] 404 Not Found - 환각 패키지 발견!")

            data = {
                "package_name": name,
                "risk_score": 85,
                "status": "PENDING",
                "score_registry": 40
            }

            try:
                # DB에 삽입
                supabase.table("packages").insert(data).execute()
                print(f"   💾 DB 저장 완료: 대시보드에 추가되었습니다!\n")
            except Exception as e:
                print(f"   ⚠️ DB 저장 실패 (이미 수집된 패키지일 수 있습니다)\n")

if __name__ == "__main__":
    run_collector()