# 실행시 터미널에 streamlit run app.py 입력 후터엔터

import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 🔐 [보안 업그레이드] 시스템 금고에서 API 키를 안전하게 가져옵니다.
# ==========================================
# 내 컴퓨터에서 테스트할 때는 물론, 배포 후에도 안전하게 키를 보호해 줍니다.
if "GEMINI_API_KEY" in st.secrets:
    # 배포용 금고(Streamlit Secrets)에서 꺼내오기
    api_key = st.secrets["GEMINI_API_KEY"]
elif "gemini" in st.session_state:
    # 임시 확인용
    api_key = st.session_state.gemini
else:
    # 혹시 모를 에러 방지용 (로컬 환경 변수 등)
    import os
    api_key = os.environ.get("GEMINI_API_KEY", "")

genai.configure(api_key=api_key)

# [모델 세팅] 이미지 분석과 채팅이 모두 가능한 최신 flash 모델 사용
model = genai.GenerativeModel('gemini-2.5-flash')

# 웹 화면 기본 설정
st.set_page_config(page_title="AI 헬스 트레이너 제임스(James)", page_icon="💪", layout="wide")
st.title("💪 AI 헬스 트레이너 제임스(James)")

# ==========================================
# 🧠 세션 상태(Session State) 초기화 (데이터 저장소)
# ==========================================
if "routine_text" not in st.session_state:
    st.session_state.routine_text = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ==========================================
# 👈 사이드바 (사용자 정보 및 목표 설정)
# ==========================================
with st.sidebar:
    st.header("👤 고객님의 신체 정보")
    gender = st.radio("성별", ["남성", "여성"])
    age = st.number_input("나이", 10, 100, 24) 
    height = st.number_input("키 (cm)", 100.0, 250.0, 170.0) # 기본값 세팅
    weight = st.number_input("몸무게 (kg)", 30.0, 200.0, 70.0) # 기본값 세팅
    
    st.divider()
    
    st.header("🎯 목표 & 경력 설정")
    # [추가 기능 1] 운동 경력 선택기
    experience = st.radio("운동 경력", ["🐣 헬린이 (맨몸/머신 위주)", "🏃‍♂️ 헬스인 (프리웨이트 병행)", "🦍 헬창 (고강도 파워리프팅)"])
    # [추가 기능 2] 다이어트 D-Day 및 기간 설정
    duration = st.slider("목표 다이어트 기간 (주)", 1, 12, 8)
    
    st.divider()

    st.header("🥗 식단 설정")
    must_eat = st.text_input("꼭 포함할 음식", placeholder="없으면 비워두세요")
    allergies = st.text_input("알레르기 음식", placeholder="없으면 비워두세요")

# ==========================================
# 🗂️ 메인 화면: 3개의 탭으로 깔끔하게 나누기
# ==========================================
tab1, tab2, tab3 = st.tabs(["📅 맞춤형 루틴 생성", "📷 식단 사진 분석", "💬 트레이너 제임스와 채팅"])

# ------------------------------------------
# 탭 1: 맞춤형 루틴 생성 및 다운로드
# ------------------------------------------
with tab1:
    st.subheader(f"🔥 {duration}주 완성 다이어트 프로젝트!")
    
    if st.button("나만의 루틴 생성하기 🚀"):
        with st.spinner("제임스가 고객님을 위한 완벽한 플랜을 짜고 있습니다..."):
            prompt = f"""
            너는 최고의 헬스 트레이너야. 아래 고객 정보를 바탕으로 {duration}주짜리 다이어트 및 운동 루틴을 마크다운으로 작성해 줘.
            
            [고객 정보]
            - 키: {height}cm, 몸무게: {weight}kg, 운동 경력: {experience}
            - 식단 필수 포함: {must_eat} / 제외: {allergies if allergies else "없음"}
            
            [출력 요구사항]
            1. 1주 차부터 {duration}주 차까지 주차별로 점진적으로 강도가 높아지는 운동 루틴 (고객의 경력 수준에 맞출 것).
            2. 각 운동의 유튜브 검색 링크 제공.
            3. 매일 먹을 수 있는 현실적인 밀프렙용 고단백 식단표.
            """
            try:
                response = model.generate_content(prompt)
                st.session_state.routine_text = response.text
                st.success("루틴이 생성되었습니다! 아래에서 확인하고 다운로드하세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

    # 루틴 결과가 있으면 화면에 출력하고 다운로드 버튼 활성화
    if st.session_state.routine_text:
        # [추가 기능 3] 나만의 루틴 다운로드 버튼 (.txt)
        st.download_button(
            label="💾 내 루틴 텍스트 파일로 다운로드",
            data=st.session_state.routine_text,
            file_name="Health_Workout_Routine.txt",
            mime="text/plain"
        )
        st.markdown(st.session_state.routine_text)

# ------------------------------------------
# 탭 2: 식단 사진 분석 (Vision AI)
# ------------------------------------------
with tab2:
    st.subheader("📷 오늘 먹을 식단을 올려주세요!")
    # [추가 기능 4] 식단 사진 업로드 및 Vision AI 분석
    uploaded_file = st.file_uploader("음식 사진을 업로드하세요 (jpg, png, jpeg)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 식단 사진", use_container_width=True)
        
        if st.button("🔍 제임스에게 칼로리 분석 맡기기"):
            with st.spinner("제임스가 사진을 뚫어져라 분석 중입니다..."):
                vision_prompt = "이 사진에 있는 음식이 무엇인지 파악하고, 대략적인 칼로리와 주요 영양 성분(탄수화물, 단백질, 지방)을 분석해서 트레이너처럼 친절하게 피드백해 줘."
                try:
                    # 이미지와 텍스트를 동시에 전송
                    vision_response = model.generate_content([vision_prompt, image])
                    st.success("분석 완료!")
                    st.markdown(vision_response.text)
                except Exception as e:
                    st.error(f"이미지 분석 중 오류가 발생했습니다: {e}")

# ------------------------------------------
# 탭 3: 트레이너 제임스와 1:1 채팅
# ------------------------------------------
with tab3:
    st.subheader("💬 궁금한 건 무엇이든 물어보세요!")
    
    # 이전 채팅 기록 화면에 뿌려주기
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # [추가 기능 5] AI 챗봇 입력창
    if prompt := st.chat_input("예: 오늘 무릎이 좀 아픈데 하체 운동 대체할 만한 거 있을까?"):
        # 1. 사용자의 질문을 화면에 표시하고 저장
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # 2. 제미(AI)의 답변 생성 및 표시
        with st.chat_message("assistant"):
            with st.spinner("제임스가 답변을 작성 중입니다..."):
                try:
                    # 챗봇용 컨텍스트(이전 대화 내용 포함)를 위해 모델 설정
                    chat = model.start_chat(history=[])
                    ai_response = chat.send_message(prompt)
                    st.markdown(ai_response.text)
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response.text})
                except Exception as e:
                    st.error("채팅 중 오류가 발생했습니다.")