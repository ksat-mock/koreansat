import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from streamlit_gsheets import GSheetsConnection
import math


# def sub_questions(row):
#     # row는 df의 각 행을 나타냅니다.
#     sub_questions_passage = [
#         row['지문평가1'],
#         row['지문평가2'],
#         row['지문평가3'],
#         row['지문평가4']
#     ]
    
#     sub_questions_problems = [
#         row['문제평가1'],
#         row['문제평가2'],
#         row['문제평가3']
#     ]
    
#     # None 값 제거
#     sub_questions_passage = [item for item in sub_questions_passage if item is not None]
#     sub_questions_problems = [item for item in sub_questions_problems if item is not None]
    
#     return sub_questions_passage, sub_questions_problems




def get_data():
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 매번 최신 데이터를 읽어오도록 설정
    df = conn.read(clear_cache=True)  # 캐시 비우고 새로 읽어오기
    
    # Print results.
    # for row in df.itertuples():
    #     st.write(f"{row.탭} has a :{row.지문}:")

    st.write(df)


    # sub_questions_TF = True
    
    # 데이터 가공
    tabs_data = {}
    for row in df.itertuples():
        tab_name = row.탭
        
        if tab_name not in tabs_data:
            tabs_data[tab_name] = {"passage": row.지문, "questions": [], "correct_answers": []}
    
        # 선지 리스트로 변환
        # choices = [row.f'선지{i}' for i in range(1, 6)]
        choices = [getattr(row, f'선지{i}') for i in range(1, 6)]


        # # 하위 문제 (지문 평가, 문제 평가) 받아오기
        # if sub_questions_TF:
        #     sub_questions_passage, sub_questions_problems = sub_questions(row)
        #     sub_questions_TF = False
        # sub_questions_passage, sub_questions_problems = sub_questions(df)
        # st.write(sub_questions_passage, sub_questions_problems)

        # 하위 문제 (지문 평가, 문제 평가) 받아오기
        if row.지문평가1:
            sub_questions_passage = [row.지문평가1, row.지문평가2, row.지문평가3, row.지문평가4]
            sub_questions_problems = [row.문제평가1, row.문제평가2, row.문제평가3, row.지문평가4]
        
        # sub_questions_passage, sub_questions_problems = sub_questions(row)
        # st.write(sub_questions_passage, sub_questions_problems)


        
        # sub_questions = []
        # sub_idx = 1
        # while True:
        #     # 하위 질문 컬럼명 생성
        #     sub_question_col = f"하위 질문{sub_idx}"        
                        
        #     #하위 질문이 있는지 확인
        #     if hasattr(row, sub_question_col) and getattr(row, sub_question_col):
        #         sub_question_text = getattr(row, sub_question_col)
                
        #         # 하위 질문 선지 처리
        #         sub_choices = []
        #         for i in range(1, 6):
        #             choice_col = f"하위 질문{sub_idx} 선지{i}"
        #             if hasattr(row, choice_col) and getattr(row, choice_col):  # 선지가 존재할 때만 추가
        #                 sub_choices.append(getattr(row, choice_col))
                
        #         # 하위 질문 정답 처리
        #         answer_col = f"하위 질문{sub_idx} 정답"
        #         sub_answer = None
        #         if hasattr(row, answer_col) and getattr(row, answer_col):  # 정답이 존재할 때만 처리
        #             sub_answer = int(getattr(row, answer_col))
                
        #         # 하위 질문 추가
        #         sub_questions.append({
        #             "question": sub_question_text,
        #             "choices": sub_choices,
        #             "answer": sub_answer
        #         })
                
        #         # 다음 하위 질문으로
        #         sub_idx += 1
        #     else:
        #         break  # 더 이상 하위 질문이 없으면 반복 종료







    
        # 질문 추가
        tabs_data[tab_name]["questions"].append({
            "question": row.질문,
            "choices": choices,
            "sub_questions_passage": sub_questions_passage,  # 하위 질문 추가 - 지문
            "sub_questions_problems": sub_questions_problems  # 하위 질문 추가 - 문제
        })
    
        # 정답 추가 (정답이 문자열일 경우 정수로 변환)
        # tabs_data[tab_name]["correct_answers"].append(int(row.정답))

        # 정답이 NaN이 아니면 정수로 변환
        correct_answer = row.정답
        if not math.isnan(correct_answer):  # NaN이 아닌지 확인
            tabs_data[tab_name]["correct_answers"].append(int(correct_answer))
    
    return tabs_data
    

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
    st.markdown(
        """
        <style>
        .horizontal-scroll {
            display: flex;
            overflow-x: auto;
            white-space: nowrap;
        }
        .horizontal-scroll > div {
            flex: 0 0 auto;
            margin-right: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    tabs_data = tabs_data = get_data()
    st.caption(tabs_data)

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

        # # 하위 문제 답안 세션 초기화
        # subquestions_key = f"subquestions_tab{tab_idx}"
        # if subquestions_key not in st.session_state:
        #     # 하위 문제를 딕셔너리로 정의하여 초기화
        #     st.session_state[subquestions_key] = {
        #         f"subq_{q_idx+1}": [None] * len(question["subquestions"])
        #         for q_idx, question in enumerate(tabs_data[tab_idx]["questions"])
        #         if "subquestions" in question  # 하위 문제가 있는 경우만 처리
        #     }

        # 하위 문제 답안 세션 초기화
        passage_key = f"subquestions_passage_tab{tab_idx}"
        problems_key = f"subquestions_problems_tab{tab_idx}"
        
        # 지문 평가 세션 초기화
        if passage_key not in st.session_state:
            st.session_state[passage_key] = {
                f"passage_q{q_idx+1}": [None] * len(question["sub_questions_passage"])
                for q_idx, question in enumerate(tabs_data[tab_idx]["questions"])
                if "sub_questions_passage" in question  # 지문 평가 질문이 있는 경우만 처리
            }
        
        # 문제 평가 세션 초기화
        if problems_key not in st.session_state:
            st.session_state[problems_key] = {
                f"problems_q{q_idx+1}": [None] * len(question["sub_questions_problems"])
                for q_idx, question in enumerate(tabs_data[tab_idx]["questions"])
                if "sub_questions_problems" in question  # 문제 평가 질문이 있는 경우만 처리
            }



    
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

        if isinstance(tab, str):
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



    
    with st.container():
        # 컬럼 비율: 지문(1.5) + 문제(1) + 하위 문제들(1씩)
        cols = st.columns([1.5, 1, 1, 1, 1, 1])
    
        # 1️⃣ 지문 (첫 번째 컬럼)
        with cols[0]:
            st.header("지문")
            st.write(passage)
    
        # 2️⃣ 문제 (두 번째 컬럼)
        questions = tabs_data[st.session_state.current_tab]["questions"]
    
        # 답안 세션 키 생성
        tab_key = f"answers_tab{st.session_state.current_tab}"
    
        # 딕셔너리로 초기화
        # if tab_key not in st.session_state:
        #     st.session_state[tab_key] = {}
    
        for idx, q in enumerate(questions):
            with cols[1]:
                st.subheader(f"문제 {idx + 1}")
                st.write(q["question"])
    
                # 문제 답변 선택
                main_key = f"main_question_{st.session_state.current_tab}_{idx}"
                selected_main = st.radio(
                    f"문제 {idx + 1}의 답을 선택하세요:",
                    q["choices"],
                    index=None,
                    key=main_key
                )
    
                # 답안 저장
                st.session_state[tab_key][idx] = (
                    q["choices"].index(selected_main) if selected_main else None
                )

            # 3️⃣ 하위 문제들 (세 번째 컬럼부터 순서대로 배치)
            sub_questions_problems = q.get("sub_questions_problems", [])
            sub_col_start = 2  # 하위 질문이 시작하는 컬럼 인덱스
            sub_col_end = len(cols)  # 컬럼의 끝 인덱스
            
            for sub_idx, sub_q in enumerate(sub_questions_problems):
                col_position = sub_col_start + sub_idx  # 순서대로 컬럼 인덱스를 계산
            
                if col_position < sub_col_end:  # 컬럼 범위를 초과하지 않도록 제한
                    with cols[col_position]:
                        st.subheader(f"{idx + 1}-{sub_idx + 1}")
                        # st.write(sub_q["question"])
                        st.write(sub_q)
            
                        # # 고유한 key 생성
                        # sub_key = f"sub_question_{st.session_state.current_tab}_{idx}_{sub_idx}"
                        # selected_sub = st.radio(
                        #     f"{idx + 1}-{sub_idx + 1}의 답을 선택하세요:",
                        #     sub_q["choices"],
                        #     index=None,
                        #     key=sub_key
                        # )

                        # 고유한 key 생성
                        sub_key = f"sub_question_{st.session_state.current_tab}_{idx}_{sub_idx}"
                        
                        # 슬라이더로 1 ~ 5 사이 점수 선택
                        selected_sub = st.slider(
                            f"{idx + 1}-{sub_idx + 1}의 답을 선택하세요:",
                            min_value=1,  # 최소 값
                            max_value=5,  # 최대 값
                            value=3,  # 기본값 (중간 값으로 설정)
                            step=1,  # 1단위로 증가
                            key=sub_key
                        )

            
                        # # 하위 문제 답안 저장
                        # if f"{idx}-sub" not in st.session_state[tab_key]:
                        #     st.session_state[tab_key][f"{idx}-sub"] = {}
                        # st.session_state[tab_key][f"{idx}-sub"][f"{sub_idx}"] = (
                        #     sub_q["choices"].index(selected_sub) if selected_sub else None
                        # )


                        # 지문 평가 답안 저장
                        for passage_q_key, sub_answers in st.session_state[passage_key].items():
                            for sub_idx, _ in enumerate(sub_answers):
                                sub_answer_key = f"{passage_q_key}_sub{sub_idx+1}"
                                st.session_state[passage_key][passage_q_key][sub_idx] = st.slider(
                                    f"지문 평가 {passage_q_key} - {sub_idx+1}",
                                    min_value=1,
                                    max_value=5,
                                    value=3,
                                    step=1,
                                    key=sub_answer_key
                                )
                        
                        # 문제 평가 답안 저장
                        for problems_q_key, sub_answers in st.session_state[problems_key].items():
                            for sub_idx, _ in enumerate(sub_answers):
                                sub_answer_key = f"{problems_q_key}_sub{sub_idx+1}"
                                st.session_state[problems_key][problems_q_key][sub_idx] = st.slider(
                                    f"문제 평가 {problems_q_key} - {sub_idx+1}",
                                    min_value=1,
                                    max_value=5,
                                    value=3,
                                    step=1,
                                    key=sub_answer_key
                                )


    
            # 3️⃣ 하위 문제들 (세 번째 컬럼부터 오른쪽에 배치)
            # sub_questions = q.get("sub_questions", [])
            # for sub_idx, sub_q in enumerate(sub_questions):
            #     col_position = sub_idx + 2  # 세 번째 컬럼부터 배치
    
            #     if col_position < len(cols):  # 컬럼 범위를 초과하지 않도록
            #         with cols[col_position]:
            #             st.subheader(f"{idx + 1}-{sub_idx + 1}")
            #             st.write(sub_q["question"])
    
            #             # 고유한 key 생성
            #             sub_key = f"sub_question_{st.session_state.current_tab}_{idx}_{sub_idx}"
            #             selected_sub = st.radio(
            #                 f"{idx + 1}-{sub_idx + 1}의 답을 선택하세요:",
            #                 sub_q["choices"],
            #                 index=None,
            #                 key=sub_key
            #             )
    
            #             # 하위 문제 답안 저장
            #             if f"{idx}-sub" not in st.session_state[tab_key]:
            #                 st.session_state[tab_key][f"{idx}-sub"] = {}
            #             st.session_state[tab_key][f"{idx}-sub"][f"{sub_idx}"] = (
            #                 sub_q["choices"].index(selected_sub) if selected_sub else None
            #             )





    

    # # 지문과 문제를 두 열로 나누기 (너비 비율 조정)
    # left_col, right_col = st.columns([3, 4])

    # # 왼쪽 열: 지문 출력
    # with left_col:
    #     st.header("지문")
    #     st.write(passage)

    # # 오른쪽 열: 문제 출력 및 답안 선택
    # with right_col:
    #     # 현재 탭에 해당하는 문제 리스트와 답안 리스트를 가져오기
    #     for idx, q in enumerate(tabs_data[st.session_state.current_tab]["questions"]):
    #         st.subheader(q["question"])
    #         selected = st.radio(f"문제 {idx + 1}의 답을 선택하세요:", q["choices"], index=None, key=f"question_{idx}")

    #         # 현재 탭에 해당하는 키에 답안을 저장
    #         tab_key = f"answers_tab{st.session_state.current_tab}"
    #         st.session_state[tab_key][idx] = q["choices"].index(selected) if selected else None

    #         st.markdown("  ")

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
