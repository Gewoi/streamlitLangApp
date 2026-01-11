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
        st.markdown(f"### {lesson["title"]}")
        st.markdown(lesson["description"])
        if st.button(label="Start Lesson", width="stretch"):
            st.session_state["nav"] = {"page": "lesson", "course_id": course_id, "current_lesson" : lesson["id"]}
            st.session_state["step_idx"] = 0
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
        st.markdown(f"### {lesson_dict["title"]}")
        st.caption(course_dict["title"])
    top_right.caption(f"Step {step_idx+1}/{len(lesson_dict["steps"])}")

    current_step = lesson_dict["steps"][step_idx]
    prompt = current_step.get("prompt", None)
    if prompt:
        st.markdown(f"__{prompt}__")

    present_container = st.container(border=True, gap="medium")
    with present_container:
        outcome = render_step(current_step)
            

    b1, b2, b3, b4 = st.columns([1, 1, 1, 3])
    back_disabled = step_idx <= 0
    next_disabled = (step_idx >= len(lesson_dict["steps"]) - 1) or (not outcome.can_go_next)


    if b1.button("⬅ Back", disabled=back_disabled):
        st.session_state["step_idx"] -= 1
        st.rerun()

    if b2.button("Skip", disabled=(step_idx >= len(lesson_dict["steps"]) - 1)):
        st.session_state["step_idx"] += 1
        st.rerun()

    if b3.button("Next ➡", disabled=next_disabled, type="primary" if not next_disabled else "secondary"):
        st.session_state["step_idx"] += 1
        st.rerun()

    #TODO: Insert a progress bar of sorts