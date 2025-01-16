import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# 📌 Google Sheets 연결 함수
def connect_to_gsheet():
    creds_json = os.getenv("GSHEET_PRIVATE_KEY").replace("\\n", "\n")
    creds_info = json.loads(creds_json)

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

# 📌 Google Sheets 데이터 불러오기
def load_tabs_data_from_gsheet():
    client = connect_to_gsheet()
    sheet_id = '1y_q2gDCyX4HhFKh2FUVowC5RH9kV3iTkYWErV-oSlIk'  # 실제 시트 ID로 변경
    worksheet_name = 'koreansat_googlesheet'

    sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    data = sheet.get_all_records()

    tabs_data = {}
    for row in data:
        tab_name = row['탭']
        if tab_name not in tabs_data:
            tabs_data[tab_name] = {"passage": row['지문'], "questions": [], "correct_answers": []}

        choices = [row[f'선지{i}'] for i in range(1, 6)]
        tabs_data[tab_name]["questions"].append({
            "question": row['질문'],
            "choices": choices
        })
        tabs_data[tab_name]["correct_answers"].append(int(row['정답']))

    return tabs_data

# ✅ 데이터 불러오기
tabs_data = load_tabs_data_from_gsheet()

# 📌 피드백 저장 함수
def save_feedback_to_gsheet(tab_name, phone_number, feedback):
    client = connect_to_gsheet()
    sheet_id = '1y_q2gDCyX4HhFKh2FUVowC5RH9kV3iTkYWErV-oSlIk'
    worksheet_name = 'feedback'

    sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    sheet.append_row([tab_name, phone_number, feedback])

# 📌 첫 번째 페이지 (전화번호 입력)
def first_page():
    st.title("전화번호 뒷자리 입력")
    phone_number = st.text_input("전화번호 뒷자리 4자리를 입력하세요:", max_chars=4)

    if st.button("다음"):
        if phone_number.isdigit() and len(phone_number) == 4:
            st.session_state.phone_number = phone_number
            st.session_state.page = "second"
            st.rerun()
        else:
            st.error("전화번호 뒷자리를 정확히 입력해주세요.")

# 📌 두 번째 페이지 (문제 풀이 및 피드백)
def second_page():
    tabs = list(tabs_data.keys())
    st.session_state.current_tab = st.session_state.get("current_tab", tabs[0])

    # 탭 버튼
    cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        if cols[i].button(tab):
            st.session_state.current_tab = tab
            st.rerun()

    current_data = tabs_data[st.session_state.current_tab]
    st.header("지문")
    st.write(current_data["passage"])

    st.header("문제")
    for idx, q in enumerate(current_data["questions"]):
        answer = st.radio(q["question"], q["choices"], key=f"{st.session_state.current_tab}_q{idx}")

    # 답안 제출
    if st.button("답안 제출하기"):
        st.success("답안이 제출되었습니다!")

    # 피드백 입력 및 제출
    feedback = st.text_area("피드백을 남겨주세요:", key=f"feedback_{st.session_state.current_tab}")
    if st.button("피드백 제출하기"):
        save_feedback_to_gsheet(st.session_state.current_tab, st.session_state.phone_number, feedback)
        st.success("피드백이 제출되었습니다!")

# 📌 페이지 관리
if "page" not in st.session_state:
    st.session_state.page = "first"

if st.session_state.page == "first":
    first_page()
elif st.session_state.page == "second":
    second_page()
