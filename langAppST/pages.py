from __future__ import annotations

import streamlit as st
from .content import get_course
from .content import load_courses, load_lessons, load_lesson_content, play_complete, find_new_exercises
from .lesson_presenter import render_step
from .progress_handler import ProgressStore


def login(email: str, password: str, supabase : ProgressStore):
    try:
        response = supabase.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state["logged_in"] = True
        return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False



def signup(email, password, store :ProgressStore):
    try:
        response = store.supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        return True
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return False


def login_page(supabase : ProgressStore):
    st.title("Welcome!")
    mode = st.radio(
        "Account",
        ["Login", "Create Account"],
        horizontal=True,
    )

    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if mode == "Create Account":
            password_repeat = st.text_input("Repeat Password", type="password")
        
        submit = st.form_submit_button(mode)

    if submit:
        if mode == "Login":
            if login(email, password, supabase):
                st.success("✅ Logged In!")
                st.rerun()
        elif mode == "Create Account":
            if password == password_repeat:
                if signup(email, password, supabase):
                    st.success("✅ Account created! Please check your email to confirm your account before logging in.")
                    st.info("After confirming, come back here and log in.")
            else:
                st.error("Passwords not the same!")
    
    st.space("small")

    st.divider()
    st.caption("Use the app as a guest. Your progress will not be saved, and you will not get recommended lessons and repetitions.")
    if st.button("Continue as Guest"):
        st.session_state["guest"] = True
        st.rerun()

def homepage():
    st.title("Language App")
    st.markdown("Pick a course!")

    course_list = load_courses()

    st.divider()

    for course in course_list:
        with st.container(border=True, key=f"bkg_image_bern_{course['id']}"):
            st.markdown(f"### {course["icon"]} {course["title"]}")
            st.markdown(course["description"])
            if st.button(label="Open Course", width="stretch", key=f"start_{course['id']}"):
                st.session_state["nav"] = {"page": "course_page", "course_id": course["id"]}
                st.session_state["step_idx"] = 0
                st.rerun()
                

def course_page(course_id : str, store : ProgressStore):
    st.title("Select Lesson")
    st.markdown("Pick a lesson!")

    course_dict = get_course(course_id)
    sections = course_dict["sections"]

    lesson_list = load_lessons(course_id)

    current_section = ""

    for lesson in lesson_list:
        if (not lesson["section"] == current_section) and (lesson["section"] in sections):
            st.divider()
            current_section = lesson["section"]
            st.title(body=f"{current_section}", text_alignment="center")
        completed_condition = store.check_lesson_completed(st.session_state["user"].id, course_id, lesson["id"])
        with st.container(border=True, key=(f"finished_lesson_{lesson['id']}" if completed_condition else f"lesson_{lesson['id']}")):
            if completed_condition:
                st.caption("Completed✅")
            st.markdown(f"### {lesson["title"]}", text_alignment="center")
            st.markdown(lesson["description"], text_alignment="center")
            if st.button(label="Start Lesson", width="stretch", key=f"start_{lesson['id']}"):
                st.session_state["nav"] = {"page": "lesson", "course_id": course_id, "current_lesson" : lesson["id"]}
                clear_lesson_sessionstate()
                st.session_state["step_idx"] = 0
                st.session_state["lesson_dict"] = lesson
                st.session_state["new_words"] = find_new_exercises(lesson)
                st.rerun()

    with st.sidebar:
        st.title("Recommended Lesson:")
        rec_lesson_id = store.get_recommended_lesson(st.session_state["user"].id, course_id)
        if rec_lesson_id:
            rec_lesson = load_lesson_content(course_id, rec_lesson_id)
            with st.container(border=True, key=f"lesson_{rec_lesson_id}_rec"):
                st.markdown(f"### {rec_lesson["title"]}", text_alignment="center")
                st.markdown(rec_lesson["description"], text_alignment="center")
                if st.button(label="Start Lesson", width="stretch", key=f"start_{lesson['id']}_rec"):
                    st.session_state["nav"] = {"page": "lesson", "course_id": course_id, "current_lesson" : rec_lesson_id}
                    clear_lesson_sessionstate()
                    st.session_state["step_idx"] = 0
                    st.session_state["lesson_dict"] = load_lesson_content(course_id, rec_lesson_id)
                    st.rerun()
        else:
            st.write("No recommendations yet")
        if store.get_known_words(st.session_state["user"].id, course_id):
            st.subheader("Repeat Random Exercises")
            with st.container(border=True, key=f"lesson_REPETITON_rec"):
                st.markdown(f"### Repetition", text_alignment="center")
                st.markdown("Repeat a random selection of exercises from your completed lessons.", text_alignment="center")
                if st.button(label="Start Lesson", width="stretch", key=f"start_REPETITION_rec"):
                    st.session_state["nav"] = {"page": "lesson", "course_id": course_id, "current_lesson" : "REPETITION"}
                    clear_lesson_sessionstate()
                    st.session_state["step_idx"] = 0
                    st.session_state["lesson_dict"] = store.generate_word_repetition(st.session_state["user"].id, course_id)
                    st.rerun()

        

def player(course_id : str, lesson_id : str, store : ProgressStore):
    course_dict = get_course(course_id)
    lesson_dict = st.session_state["lesson_dict"]
    step_idx = st.session_state["step_idx"]

    top_left, top_mid, top_right = st.columns([2, 3.5, 1], vertical_alignment="bottom")
    if top_left.button("⬅ Lessons"):
        st.session_state["nav"] = {"page": "course_page", "course_id": course_id}
        st.rerun()
    with top_mid:
        st.markdown(f"#### {lesson_dict["title"]}")
        st.caption(course_dict["title"])
    top_right.caption(f"Step {step_idx+1}/{len(lesson_dict["steps"])}")
    st.progress( round((step_idx+1) / len(lesson_dict["steps"]) * 100))

    st.space("small")

    current_step = lesson_dict["steps"][step_idx]
    prompt = current_step.get("prompt", None)
    if prompt:
        st.markdown(f"#### :blue[{prompt}]", text_alignment="center")

    st.space("small")
    present_container = st.container(border=True, gap="small")
    with present_container:
        outcome = render_step(current_step)

            

    b1, b2, b3 = st.columns(3)
    back_disabled = step_idx <= 0
    last_condition = (step_idx >= len(lesson_dict["steps"]) - 1)
    next_disabled = (not outcome.can_go_next)

    if b1.button("⬅ Back", disabled=back_disabled):
        st.session_state["step_idx"] -= 1
        reset_select_sessionstate()
        st.rerun()

    if not last_condition:
        if b2.button("Skip"):
            st.session_state["step_idx"] += 1
            reset_select_sessionstate()
            st.rerun()
    
        if b3.button("Next ➡", disabled=next_disabled, width="stretch"):
            st.session_state["step_idx"] += 1
            reset_select_sessionstate()
            st.rerun()
    else:
        if b3.button(label="Finish Lesson", type="primary", disabled=next_disabled):
            st.session_state["nav"] = {"page": "finish", "course_id": course_id, "current_lesson": lesson_id}
            st.rerun()
            

def finishing_screen(course_id : str, lesson_id : str, store : ProgressStore):
    with st.container(border=True):
        st.title("Congratulations! :balloon:", text_alignment="center")
        st.markdown(f"### You finished the lesson!", text_alignment="center")
        st.space("large")
        st.balloons()
        play_complete()
        if st.button(label="continue", width= "stretch", type="primary"):
            st.session_state["nav"] = {"page": "course_page", "course_id": course_id}
            if not lesson_id == "REPETITION":
                store.lesson_completed(st.session_state["user"].id, course_id, lesson_id, st.session_state["mistakes"], st.session_state["new_words"])
            clear_lesson_sessionstate()
            st.rerun()


def clear_lesson_sessionstate():
    st.session_state["pressed_match_buttons"] = []
    st.session_state["match_sel_btn"] = None
    st.session_state["left"] = []
    st.session_state["right"] = []
    st.session_state["order_tokens"] = []
    st.session_state["used_tokens"] = []
    st.session_state["order_answer"] = []
    st.session_state["mistakes"] = 0
    st.session_state["new_words"] = []
    st.session_state["take_over_answer"] = ""
    st.session_state["lesson_dict"] = {}
    st.session_state["correct_order"] = []
    st.session_state["last_pair"] = []
    st.session_state["match_sound"] = ""
    st.session_state["exercise_done"] = False

def reset_select_sessionstate():
    st.session_state["order_tokens"] = []
    st.session_state["used_tokens"] = []
    st.session_state["order_answer"] = []
    st.session_state["correct_order"] = []
    st.session_state["exercise_done"] = False