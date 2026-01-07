from __future__ import annotations

import streamlit as st
from .content import get_course
from .content import load_courses, load_lessons, load_lesson_content

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
            st.rerun()

def player(course_id : str, lesson_id : str):
    course_dict = get_course(course_id)
    lesson_dict = load_lesson_content(course_id, lesson_id)
    st.title(lesson_dict["title"])
    st.caption(course_dict["title"])

    top_left, top_mid, top_right = st.columns([1, 2, 1])
    if top_left.button("⬅ Lessons"):
        st.session_state["nav"] = {"page": "course", "course_id": course_id}
        st.rerun()

