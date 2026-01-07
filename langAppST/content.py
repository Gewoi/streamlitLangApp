from __future__ import annotations

import streamlit as st
import glob

from pathlib import Path
import yaml

COURSES_ROOT = Path("data") / "courses"

def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

@st.cache_data(show_spinner=False)
def load_courses():
    course_list = []
    for course_yaml in sorted(COURSES_ROOT.glob("*/course.yaml")):
        course_data = read_yaml(course_yaml)
        course_list.append(course_data)
    return course_list

@st.cache_data(show_spinner=False)
def load_lessons(course_id : str):
    course_dir = COURSES_ROOT / course_id
    lesson_list = []
    for lesson_yaml in sorted(course_dir.glob("lessons/*.yaml")):
        lesson_data = read_yaml(lesson_yaml)
        lesson_list.append(lesson_data)
    return lesson_list

@st.cache_data(show_spinner=False)
def load_lesson_content(course_id : str, lesson_id : str):
    course_dir = COURSES_ROOT / course_id
    lesson_yaml_p = course_dir / "lessons" / str(lesson_id + ".yaml") 
    lesson_dict = read_yaml(lesson_yaml_p)
    return lesson_dict

def get_course(course_id : str):
    course_yaml = COURSES_ROOT / course_id / "course.yaml"
    course_dict = read_yaml(course_yaml)
    return course_dict