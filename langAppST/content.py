from __future__ import annotations

import streamlit as st
import glob
import cv2
import random

from pathlib import Path
import yaml

COURSES_ROOT = Path("data") / "courses"

DEFAULT_TARGET_SIZE = (350, 300)

def autoplay_sound(sound_path):
    with st.container(key=f"sound_fx_{random.randint(0,4000)}", width=1):
        st.audio(sound_path, autoplay=True)

@st.cache_data(show_spinner=False)
def play_correct():
    autoplay_sound("data/assets/audio/correct_exercise.wav")

@st.cache_data(show_spinner=False)
def play_wrong():
    autoplay_sound("data/assets/audio/wrong_exercise.wav")

@st.cache_data(show_spinner=False)
def play_match_correct():
    autoplay_sound("data/assets/audio/match_correct.wav")

@st.cache_data(show_spinner=False)
def play_complete():
    autoplay_sound("data/assets/audio/lesson_done.wav")

@st.cache_data(show_spinner=False)
def contain_cv2(img, target_w, target_h, allow_upscale=False):
    h, w = img.shape[:2]

    scale_w = target_w / w
    scale_h = target_h / h
    scale = min(scale_w, scale_h)

    if not allow_upscale:
        scale = min(scale, 1.0)

    new_w = int(round(w * scale))
    new_h = int(round(h * scale))

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized

@st.cache_data(show_spinner=False)
def resize_image(img_path, target_size = DEFAULT_TARGET_SIZE):
    image = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    resized = contain_cv2(img_rgb, target_size[0], target_size[1])
    return resized

def read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data

@st.cache_data(show_spinner=False, ttl="1d")
def load_courses():
    course_list = []
    for course_yaml in sorted(COURSES_ROOT.glob("*/course.yaml")):
        course_data = read_yaml(course_yaml)
        course_list.append(course_data)
    return course_list

@st.cache_data(show_spinner=False, ttl="1d")
def load_lessons(course_id : str):
    course_dir = COURSES_ROOT / course_id
    lesson_list = []
    for lesson_yaml in sorted(course_dir.glob("lessons/*.yaml")):
        lesson_data = read_yaml(lesson_yaml)
        lesson_list.append(lesson_data)
    return lesson_list

@st.cache_data(show_spinner=False, ttl="1d")
def load_lesson_content(course_id : str, lesson_id : str):

    course_dir = COURSES_ROOT / course_id
    lesson_yaml_p = course_dir / "lessons" / str(lesson_id + ".yaml") 
    lesson_dict = read_yaml(lesson_yaml_p)

    return lesson_dict

def get_course(course_id : str):
    course_yaml = COURSES_ROOT / course_id / "course.yaml"
    course_dict = read_yaml(course_yaml)
    return course_dict

def find_new_exercises(lesson_dict : dict):
    included_steps = ["cloze", "order", "translate_type", "listen_type", "true_false", "match"]
    steps = []

    for step in lesson_dict["steps"]:
        if step["type"] in included_steps:
            steps.append(step)
    return steps

def create_section_repetition(course_id : str, section : str):
    included_steps = ["cloze", "order", "translate_type", "listen_type", "true_false", "match"]

    lesson_list = load_lessons(course_id)
    possible_exercises = []
    for lesson in lesson_list:
        if lesson["section"] == section:
            for step in lesson["steps"]:
                if step["type"] in included_steps:
                    possible_exercises.append(step)

    number = min(len(possible_exercises), 10)
    random.shuffle(possible_exercises)
    chosen_exercises = possible_exercises[:number]

    lesson_dict = {"id": "REPETITION","title": "Repeat some Words!", "description": "Repeat a random selection of words", "steps" : []}

    for exercise in chosen_exercises:
        lesson_dict["steps"].append(exercise)
    
    return lesson_dict
