from __future__ import annotations

import streamlit as st
import os
from dataclasses import dataclass
import pathlib as Path

import random

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
    original_sentence = sentence_data.get("question", None)
    goal_sentence_arr = sentence_data["target"]
    helper_sentence = sentence_data.get("helper", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(sol.casefold())

    audio = step.get("audio",None)
    images = step.get("images",None)
    #st.space("small")
    with st.form("answer", border=False):
        if original_sentence:
            st.markdown(f"__{original_sentence}__", text_alignment="center")
        if helper_sentence:
            st.caption(helper_sentence, text_alignment="center")
        if images:
            for img in images:
                if os.path.exists(img):
                    st.image(img)
        if audio:
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

        answer = st.text_input("answer", autocomplete="off", label_visibility="hidden")
        submitted = st.form_submit_button("Check", width="stretch")


    #st.space("small")
    if submitted:
        if answer.casefold() in caseIns_solutions:
            st.success("Correct ✅")
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)

def render_order(step: dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data.get("question", None)
    helper_sentence = sentence_data.get("helper", None)
    if not st.session_state["order_tokens"]:
        tokens = step["tokens"]
        random.shuffle(tokens)
        st.session_state["order_tokens"] = tokens
        used_tokens = []
    else:
        tokens = st.session_state["order_tokens"]
        used_tokens = st.session_state["used_tokens"]

    solutions = step["answers"]

    audio = step.get("audio", None)
    images = step.get("images", None)


    if original_sentence:
        st.markdown(f"__{original_sentence}__", text_alignment="center")
    if helper_sentence:
        st.caption(helper_sentence, text_alignment="center")
    if images:
        for img in images:
            if os.path.exists(img):
                st.image(img)
    if audio:
        if os.path.exists(audio):
            st.audio(audio)
    else:
        st.info(f"(Missing audio asset: {audio})")
    #TODO: Better formatting!!

    st.divider()
    answer = st.session_state["order_answer"]
    st.markdown(f"#### {answer}", text_alignment="center")
    st.divider()
    tempCols = st.columns(3, vertical_alignment="center")
    with tempCols[1]:
        if st.button("Undo", type="primary", width="stretch"):
            st.session_state["order_answer"] = ""
            st.session_state["used_tokens"] = []
            st.rerun()
    
    
    cols = st.columns(len(tokens))
    for i, col in enumerate(cols):
        with cols[i % 5]:
            button_disabled = tokens[i] in used_tokens
            if st.button(label=tokens[i], disabled=button_disabled):
                st.session_state["used_tokens"] = used_tokens + [tokens[i]]
                st.session_state["order_answer"] += "  " + tokens[i] if not answer == "" else tokens[i]
                st.rerun()
    st.divider()
    st.space("small")
    with st.form("answer", border=False):
        submitted = st.form_submit_button("Check", width="stretch")
    
    
            

    if submitted:
        if answer in solutions:
            st.success("Correct ✅")
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)