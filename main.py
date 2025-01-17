import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read()

# Print results.
for row in df.itertuples():
    st.write(f"{row.탭]} has a :{row.지문}:")

# 데이터 가공
tabs_data = {}
for row in df:
    tab_name = row['탭']
    if tab_name not in tabs_data:
        tabs_data[tab_name] = {"passage": row['지문'], "questions": [], "correct_answers": []}

    # 선지 리스트로 변환
    choices = [row[f'선지{i}'] for i in range(1, 6)]

    # 질문 추가
    tabs_data[tab_name]["questions"].append({
        "question": row['질문'],
        "choices": choices
    })

    # 정답 추가 (정답이 문자열일 경우 정수로 변환)
    tabs_data[tab_name]["correct_answers"].append(int(row['정답']))


# tabs_data = load_tabs_data_from_gsheet()
    

# Google Sheets 연동 함수
# def connect_to_gsheet():
#     creds_json = os.getenv("GSHEET_PRIVATE_KEY").replace("\\n", "\n")
#     creds_info = json.loads(creds_json)

#     # 인증 범위
#     SCOPES = [
#         'https://www.googleapis.com/auth/spreadsheets',
#         'https://www.googleapis.com/auth/drive'
#     ]

#     creds = Credentials.from_service_account_info(creds_info)
#     client = gspread.authorize(creds)
#     return client

# # Google Sheets에서 데이터 불러오기
# def load_tabs_data_from_gsheet():
#     tabs_data = {}

#     # Google Sheets 연결
#     client = connect_to_gsheet()

#     # 시트 ID와 워크시트 이름을 입력해야 함
#     sheet_id = '1y_q2gDCyX4HhFKh2FUVowC5RH9kV3iTkYWErV-oSlIk'  # 여기에 시트 ID 입력
#     worksheet_name = 'koreansat_googlesheet'  # 워크시트 이름 (시트 하단 탭 이름)

#     # 시트 열기
#     sheet = client.open_by_key(sheet_id).worksheet(worksheet_name)

#     # 데이터 불러오기
#     data = sheet.get_all_records()

#     # 데이터 가공
#     for row in data:
#         tab_name = row['탭']
#         if tab_name not in tabs_data:
#             tabs_data[tab_name] = {"passage": row['지문'], "questions": [], "correct_answers": []}

#         # 선지 리스트로 변환
#         choices = [row[f'선지{i}'] for i in range(1, 6)]

#         # 질문 추가
#         tabs_data[tab_name]["questions"].append({
#             "question": row['질문'],
#             "choices": choices
#         })

#         # 정답 추가 (정답이 문자열일 경우 정수로 변환)
#         tabs_data[tab_name]["correct_answers"].append(int(row['정답']))

#     return tabs_data

# tabs_data = load_tabs_data_from_gsheet()


##########################################################
##########################################################


# 첫 번째 페이지: 전화번호 뒷자리 4자리를 입력 받는 페이지
def first_page():
    st.title("전화번호 뒷자리 입력")

    phone_number = st.text_input("전화번호 뒷자리 4자리를 입력하세요:", max_chars=4)

    if st.button("다음"):
        if phone_number and phone_number.isdigit() and len(str(phone_number)) == 4:
            st.session_state.phone_number = phone_number
            st.session_state.page = "second"  # 두 번째 페이지로 이동
            st.rerun()  # 페이지 강제 새로고침
        else:
            st.error("전화번호 뒷자리 4자리를 정확하게 입력하세요.")


# 두 번째 페이지: 문제 풀이 페이지
def second_page():
    st.set_page_config(layout="wide")

    # 탭 세션 관리
    tabs = list(tabs_data.keys())

    if "current_tab" not in st.session_state:
        st.session_state.current_tab = tabs[0]

    if "completed_tabs" not in st.session_state:
        st.session_state.completed_tabs = set()

    # 사용자 답안을 저장할 리스트 (Session State 사용) - 탭 개수만큼 답안 세션 관리
    # tab_count = 7  # 예시로 7개의 탭이 있다고 가정

    # for tab_idx in range(1, tab_count + 1):
    for tab_idx in tabs:
        tab_key = f"answers_tab{tab_idx}"
        if tab_key not in st.session_state:
            # 각 탭에 대해 문제의 개수에 맞는 사용자 답안을 저장할 리스트 초기화
            # st.session_state[tab_key] = [None] * len(questions[tab_idx - 1])  # questions[tab_idx - 1]는 탭에 맞는 문제 리스트
            st.session_state[tab_key] = [None] * len(tabs_data[tab_idx]["questions"])  # 탭에 맞는 문제 리스트

        submitted_key = f"submitted_tab{tab_idx}"
        if submitted_key not in st.session_state:
            # 각 탭에 대해 제출 여부 상태 초기화
            st.session_state[submitted_key] = False

        submitted_key_2 = f"submitted_tab{tab_idx}_2"
        if submitted_key_2 not in st.session_state:
            # 각 탭에 대해 제출 여부 상태 초기화
            st.session_state[submitted_key_2] = 0

        correct_status_key = f"correct_status_tab{tab_idx}"
        if correct_status_key not in st.session_state:
            st.session_state[correct_status_key] = [None] * len(tabs_data[tab_idx]["questions"])  # 각 문제별 정답 여부 초기화


    # 평가 기준 설명
    st.markdown("##### 다음 평가 기준에 따라 4개의 수능 국어 지문/문제를 평가해주세요")
    # st.subheader("아래 4개의 수능 국어 문제를 풀고, 다음 평가 기준에 따라 평가해주세요")

    # 평가 기준 설명
    left_col_eval, right_col_eval = st.columns([3, 4])

    # 왼쪽 열: 지문 평가 기준
    with left_col_eval:
        st.write("[지문 평가 기준] ")
        st.write("・  ")
        st.write("・  ")

    # 오른쪽 열: 문제 평가 기준
    with right_col_eval:
        st.write("[문제 평가 기준] ")
        st.write("・  ")
        st.write("・  ")

    st.markdown("  ")

    # 버튼 표시
    cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        style = (
            "border: 2px solid pink; background-color: lightgreen;"
            if tab == st.session_state.current_tab
            else ""
        )

        if cols[i].button(tab, key=f"tab_button_{i}"):
            st.session_state.current_tab = tab

    current_data = tabs_data[st.session_state.current_tab]
    passage = current_data["passage"]
    questions = current_data["questions"]

    # 가로 선 추가
    st.divider()

    # 타이틀
    st.markdown("  ")
    st.title("국어 영역")
    st.markdown("  ")

    # 지문과 문제를 두 열로 나누기 (너비 비율 조정)
    left_col, right_col = st.columns([3, 4])

    # 왼쪽 열: 지문 출력
    with left_col:
        st.header("지문")
        st.write(passage)

    # 오른쪽 열: 문제 출력 및 답안 선택
    with right_col:
        # 현재 탭에 해당하는 문제 리스트와 답안 리스트를 가져오기
        for idx, q in enumerate(tabs_data[st.session_state.current_tab]["questions"]):
            st.subheader(q["question"])
            selected = st.radio(f"문제 {idx + 1}의 답을 선택하세요:", q["choices"], index=None, key=f"question_{idx}")

            # 현재 탭에 해당하는 키에 답안을 저장
            tab_key = f"answers_tab{st.session_state.current_tab}"
            st.session_state[tab_key][idx] = q["choices"].index(selected) if selected else None

            st.markdown("  ")

    # 제출 버튼
    if st.button("답안 제출하기"):
        submitted_key = f"submitted_tab{st.session_state.current_tab}"
        st.session_state[submitted_key] = True
        submitted_key_2 = f"submitted_tab{st.session_state.current_tab}_2"
        st.session_state[submitted_key_2] += 1

    if st.session_state.get(f"submitted_tab{st.session_state.current_tab}", False):
        st.success("답안이 제출되었습니다!")

        # 지문과 문제를 두 열로 나누기 (너비 비율 조정)
        left_col_2, right_col_2 = st.columns([3, 4])

        with left_col_2:
            # 선택한 답안 표시
            # st.subheader("선택한 답안:")
            tab_key = f"answers_tab{st.session_state.current_tab}"

            for idx, answer in enumerate(st.session_state[tab_key]):
                selected_choice = answer + 1 if answer is not None else "선택 안 함"
                # st.write(f"문제 {idx + 1}: {selected_choice}")
            st.write("   ")

        with right_col_2:
            # 답안 비교 및 정답 확인
            # st.subheader("정답 확인:")

            # 탭에 해당하는 correct_answers 가져오기
            correct_answers = tabs_data[st.session_state.current_tab]["correct_answers"]
            tab_key = f"answers_tab{st.session_state.current_tab}"
            correct_status_key = f"correct_status_tab{st.session_state.current_tab}"

            # 제출한 답안과 정답 비교
            result = []
            for idx, answer in enumerate(st.session_state[tab_key]):
                # 정답 여부를 correct_status에 저장
                is_correct = answer == correct_answers[idx] -1
                st.session_state[correct_status_key][idx] = is_correct

                correct = "맞았습니다" if is_correct else "틀렸습니다"
                # st.write(f"문제 {idx + 1}: {correct}")
                result.append(f"문제 {idx + 1}: {correct}")

            st.session_state[submitted_key] = False

    if st.session_state[submitted_key] == False and st.session_state[f"submitted_tab{st.session_state.current_tab}_2"] > 0:
        # st.info를 사용하여 결과를 표시
        # st.info("\n".join(result))  # 정답 여부를 한 번에 보여줌
        # st.info(st.session_state[f'correct_status_tab{st.session_state.current_tab}'])
        for idx, each_result in enumerate(st.session_state[f'correct_status_tab{st.session_state.current_tab}']):
            if each_result == False:
                st.info(f"문제 {idx + 1}: 틀렸습니다.")
            else:
                st.info(f"문제 {idx + 1}: 맞았습니다.")

    st.write("   ")

    # 피드백 제출 처리 함수
    def submit_feedback():
        feedback_input = st.session_state[f"feedback_input_{st.session_state.current_tab}"].strip()
        if feedback_input:
            # 현재 탭에 맞는 피드백과 제출 상태를 저장
            feedback_key = f"feedback_tab{st.session_state.current_tab}"
            feedback_submitted_key = f"feedback_submitted_tab{st.session_state.current_tab}"

            st.session_state[feedback_key] = feedback_input  # 입력 내용 저장
            st.session_state[feedback_submitted_key] = True  # 제출 상태 업데이트
        else:
            st.warning("피드백을 입력해주세요.")

    # 각 탭에 대한 피드백 세션 상태 초기화
    if f'feedback_submitted_tab{st.session_state.current_tab}' not in st.session_state:
        st.session_state[f'feedback_submitted_tab{st.session_state.current_tab}'] = False

    if f'feedback_tab{st.session_state.current_tab}' not in st.session_state:
        st.session_state[f'feedback_tab{st.session_state.current_tab}'] = ""

    # 가로 선 추가
    st.divider()

    # 피드백 입력 필드 (제출 후에도 유지)
    st.write("   ")
    st.write("   ")
    st.write("   ")
    st.subheader(f"{st.session_state.current_tab} 탭 피드백을 남겨주세요.")  # 현재 탭에 맞는 제목

    # 각 탭별로 고유한 key를 설정하여 피드백 입력 창 만들기
    feedback_input_key = f"feedback_input_{st.session_state.current_tab}"
    st.text_area("의견을 남겨주세요:", key=feedback_input_key)

    # 피드백 제출 버튼 (콜백 함수 연결)
    st.button("피드백 제출하기", on_click=submit_feedback)

    # 피드백 제출 완료 메시지 및 입력한 내용 표시
    if st.session_state[f'feedback_submitted_tab{st.session_state.current_tab}']:
        # st.success("피드백이 제출되었습니다!")
        st.write("남겨주신 피드백:")
        st.info(st.session_state[f'feedback_tab{st.session_state.current_tab}'])  # 저장된 피드백 출력


# 페이지 관리
if 'page' not in st.session_state:
    st.session_state.page = "first"  # 첫 번째 페이지로 시작

# 페이지 전환
if st.session_state.page == "first":
    first_page()
elif st.session_state.page == "second":
    second_page()
