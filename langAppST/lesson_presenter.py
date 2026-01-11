from __future__ import annotations

import streamlit as st
import os
from dataclasses import dataclass
import pathlib as Path

@dataclass
class StepOutcome:
    can_go_next: bool

def render_step(step : dict):
    stype = str(step.get("type", "markdown"))
    if stype == "markdown":
        return render_markdown(step)
    if stype == "cloze":     
        return render_cloze(step)
    if stype == "order":
        return render_order(step)
    # if stype == "listen_type":
    #     return render_listen_type(step, course=course, lesson=lesson, course_id=course_id)
    # if stype == "pronounce":
    #     return render_pronounce(step, course=course, lesson=lesson, course_id=course_id)
    # if stype == "match":
    #     return render_match(step, course=course, lesson=lesson, course_id=course_id)
    # st.warning(f"Unknown step type: {stype!r}")
    # return StepOutcome(can_go_next=True)

def render_markdown(step : dict):
    st.markdown(step.get("markdown", "no markdown found"))

    images = step.get("images", [])
    for img in images or []:
        if os.path.exists(img):
            st.image(str(img))
        else:
            st.info(f"(Missing image asset: {img})")

    return StepOutcome(can_go_next=True)

#TODO: Write all the render functions

def render_cloze(step: dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data["question"] or None
    goal_sentence_arr = sentence_data["target"]
    helper_sentence = sentence_data["helper"] or None
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(sol.casefold())

    audio = step["audio"]
    images = step["images"]
    #st.space("small")
    with st.form("answer", border=False):
        if original_sentence:
            st.markdown(f"__{original_sentence}__", text_alignment="center")
        if helper_sentence:
            st.caption(helper_sentence, text_alignment="center")
        for img in images:
            if os.path.exists(img):
                st.image(img)
        if os.path.exists(audio):
            st.audio(audio)
        else:
            st.info(f"(Missing audio asset: {audio})")
        
        st.space("small")
    
        blank_space = ""
        for i in range(len(solutions[0])):
            blank_space += "_"
            
        full_question_sentence = str(goal_sentence_arr[0] + blank_space + goal_sentence_arr[1])
        st.markdown(f"_{full_question_sentence}_")

        answer = st.text_input("", autocomplete="off")
        submitted = st.form_submit_button("Check")


    #st.space("small")
    if submitted:
        if answer.casefold() in caseIns_solutions:
            st.success("Correct ✅")
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)

def render_order(step: dict):
    st.write("rendering order now")
    return StepOutcome(can_go_next=True)