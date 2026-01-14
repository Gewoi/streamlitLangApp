from __future__ import annotations

import streamlit as st
from .content import get_course
from .content import load_courses, load_lessons, load_lesson_content
from .lesson_presenter import render_step

def homepage():
    st.title("Language App")
    st.markdown("Pick a course!")

    course_list = load_courses()

    for course in course_list:
        st.divider()
        st.markdown(f"### {course["icon"]} {course["title"]}")
        st.markdown(course["description"])
        if st.button(label="Open Course", width="stretch"):
            st.session_state["nav"] = {"page": "course_page", "course_id": course["id"]}
            st.rerun()

def course_page(course_id : str):
    st.title("Select Lesson")
    st.markdown("Pick a lesson!")

    lesson_list = load_lessons(course_id)

    for lesson in lesson_list:
        st.divider()
        with st.container(border=True):
            st.markdown(f"### {lesson["title"]}", text_alignment="center")
            st.markdown(lesson["description"], text_alignment="center")
            if st.button(label="Start Lesson", width="stretch"):
                st.session_state["nav"] = {"page": "lesson", "course_id": course_id, "current_lesson" : lesson["id"]}
                st.session_state["step_idx"] = 0
                st.session_state["order_tokens"] = []
                st.session_state["used_tokens"] = []
                st.session_state["order_answer"] = []

                st.session_state["left"] = []
                st.session_state["right"] = []
                st.session_state["pressed_match_buttons"] = []
                st.session_state["match_sel_btn"] = None
                st.rerun()

def player(course_id : str, lesson_id : str):
    course_dict = get_course(course_id)
    lesson_dict = load_lesson_content(course_id, lesson_id)

    step_idx = st.session_state["step_idx"]

    top_left, top_mid, top_right = st.columns([2, 3.5, 1], vertical_alignment="bottom")
    if top_left.button("⬅ Lessons"):
        st.session_state["nav"] = {"page": "course_page", "course_id": course_id}
        st.rerun()
    with top_mid:
        st.markdown(f"#### {lesson_dict["title"]}")
        st.caption(course_dict["title"])
    top_right.caption(f"Step {step_idx+1}/{len(lesson_dict["steps"])}")

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
        st.rerun()

    if not last_condition:
        if b2.button("Skip"):
            st.session_state["step_idx"] += 1
            clear_lesson_sessionstate()
            st.rerun()
    
        if b3.button("Next ➡", disabled=next_disabled):
            st.session_state["step_idx"] += 1
            clear_lesson_sessionstate()
            st.rerun()
    else:
        if b3.button(label="Finish Lesson", type="primary", disabled=next_disabled):
            st.session_state["nav"] = {"page": "finish", "course_id": course_id, "current_lesson": lesson_id}
            st.rerun()
            

    #TODO: Insert a progress bar of sorts

def finishing_screen(course_id : str, lesson_id : str):
    with st.container(border=True):
        st.title("Congratulations! :balloon:", text_alignment="center")
        st.markdown(f"### You finished the lesson!", text_alignment="center")
        st.space("large")
        if st.button(label="continue", width= "stretch", type="primary"):
            st.session_state["nav"] = {"page": "course_page", "course_id": course_id}
            st.rerun()


def clear_lesson_sessionstate():
    st.session_state["pressed_match_buttons"] = []
    st.session_state["match_sel_btn"] = None
    st.session_state["left"] = []
    st.session_state["right"] = []
    st.session_state["order_tokens"] = []
    st.session_state["used_tokens"] = []
    st.session_state["order_answer"] = []