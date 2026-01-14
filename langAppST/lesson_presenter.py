from __future__ import annotations

import streamlit as st
import streamlit_extras as ste
import os
from dataclasses import dataclass
import pathlib as Path
from string import ascii_letters

import random

@dataclass
class StepOutcome:
    can_go_next: bool

def comparison_string(input_string : str):
    result = ''.join([letter for letter in input_string if letter in ascii_letters])
    result = result.casefold()
    return result

def render_step(step : dict):
    stype = str(step.get("type", "markdown"))
    if stype == "markdown":
        return render_markdown(step)
    if stype == "cloze":     
        return render_cloze(step)
    if stype == "order":
        return render_order(step)
    if stype == "translate_type":
        return render_translate_type(step)
    if stype == "listen_type":
        return render_listen_type(step)
    if stype == "match":
        return render_match(step)
    if stype == "true_false":
        return render_true_false(step)
    st.warning(f"Unknown step type: {stype!r}")
    return StepOutcome(can_go_next=True)

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

    sol_display = step.get("solutions_display", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(comparison_string(sol))

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
        if comparison_string(answer) in caseIns_solutions:
            if sol_display:
                st.success(sol_display)
            else:
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

    solutions = step["tokens"]

    audio = step.get("audio", None)
    images = step.get("images", None)

    sol_display = step.get("solution_display", None)


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
    answer = ""
    for elm in st.session_state["order_answer"]:
        answer += " " + str(elm)
    st.markdown(f"#### {answer}", text_alignment="center")
    st.divider()
    tempCols = st.columns(3, vertical_alignment="center")
    with tempCols[1]:
        if st.button("Undo", type="primary", width="stretch"):
            st.session_state["order_answer"] = []
            st.session_state["used_tokens"] = []
            st.rerun()
    
    
    cols = st.columns(len(tokens))
    for i, col in enumerate(cols):
        with cols[i % 5]:
            button_disabled = tokens[i] in used_tokens
            if st.button(label=tokens[i], disabled=button_disabled):
                st.session_state["used_tokens"] += [tokens[i]]
                st.session_state["order_answer"] += [tokens[i]]
                st.rerun()
    st.divider()
    with st.form("answer", border=False):
        submitted = st.form_submit_button("Check", width="stretch")

    if submitted:
        if st.session_state["order_answer"] == solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            st.session_state["order_tokens"] = []
            st.session_state["used_tokens"] = []
            st.session_state["order_answer"] = []
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")
    return StepOutcome(can_go_next=False)

def render_translate_type(step : dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data.get("question", None)
    helper_sentence = sentence_data.get("helper", None)

    sol_display = step.get("solutions_display", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(comparison_string(sol))

    audio = step.get("audio", None)
    images = step.get("images", None)

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

        answer = st.text_input("answer", label_visibility="hidden", autocomplete="off")
        
        submitted = st.form_submit_button("Check", width="stretch")
    
    if submitted:
        if comparison_string(answer) in caseIns_solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)



def render_listen_type(step : dict):
    sol_display = step.get("solutions_display", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(comparison_string(sol))

    audio = step["audio"]
    images = step.get("images", None)

    #st.space("small")
    with st.form("answer", border=False):
        if images:
            for img in images:
                if os.path.exists(img):
                    st.image(img)
        if os.path.exists(audio):
            st.audio(audio)
        else:
            st.info(f"(Missing audio asset: {audio})")

        answer = st.text_input("answer", label_visibility="hidden", autocomplete="off")
        
        submitted = st.form_submit_button("Check", width="stretch")
    
    if submitted:
        if comparison_string(answer) in caseIns_solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            return StepOutcome(can_go_next=True)
        else:
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)

def render_match(step : dict):

    #TODO: Probabliy works better with stateful button!!!!!

    pairs = step["pairs"]
    all_buttons = []
    for pair in pairs:
        all_buttons.append(pair["right"]["target"])
        all_buttons.append(pair["left"]["original"])
    if not st.session_state["left"]:
        left = [el["left"] for el in pairs]
        random.shuffle(left)
        st.session_state["left"] = left
    else:
        left = st.session_state["left"]
    if not st.session_state["right"]:
        right = [el["right"] for el in pairs]
        random.shuffle(right)
        st.session_state["right"] = right
        pressed_match_btns = []
    else:
        right = st.session_state["right"]
        pressed_match_btns = st.session_state["pressed_match_buttons"]
    match_sel_btn = st.session_state["match_sel_btn"]
    corresponding_btn = ""
    for pair in pairs:
        if pair["left"]["original"] == match_sel_btn:
            corresponding_btn = pair["right"]["target"]
            break
        elif pair["right"]["target"] == match_sel_btn:
            corresponding_btn = pair["left"]["original"]
            break
    
    def check_buttons(lang : str):
        if match_sel_btn:
            if elm[lang] == corresponding_btn:
                st.session_state["pressed_match_buttons"] += [elm[lang], match_sel_btn]
                st.session_state["match_sel_btn"] = None
                st.rerun()
            else:
                st.session_state["match_sel_btn"] = None
                st.rerun()
        else:
            st.session_state["match_sel_btn"] = elm[lang]
            st.rerun()

    cols = st.columns([2,1,2], gap="medium")
    for elm in left:
        disable_cond = elm["original"] in pressed_match_btns or elm["original"] == match_sel_btn
        if cols[0].button(label = f":orange-background[**{elm["original"]}**]" if elm["original"] is match_sel_btn else elm["original"], width="stretch", disabled=disable_cond):
            check_buttons("original")
    for elm in right:
        disable_cond = elm["target"] in pressed_match_btns or elm["target"] == match_sel_btn
        if cols[2].button(label = f":orange-background[**{elm["target"]}**]" if elm["target"] is match_sel_btn else elm["target"], width="stretch", disabled=disable_cond):
            check_buttons("target")

    if st.session_state["pressed_match_buttons"] == all_buttons:
        st.success("Correct ✅")
        return StepOutcome(can_go_next=True)

    return StepOutcome(can_go_next=False)

def render_true_false(step: dict):
    audio = step.get("audio", None)
    images = step.get("images", None)
    sol_display = step.get("solution_display", None)
    display_text = step["text"]

    answer = step["answer"]

    if audio:
        if os.path.exists(audio):
            st.audio(audio)
        else:
            st.info(f"(Missing audio asset: {audio})")
    if images:
            for img in images:
                if os.path.exists(img):
                    st.image(img)
    st.markdown(f"### {display_text}", text_alignment="center")

    def check_answer(label):
        if answer == label:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            return True
        else:
            st.error("Not quite. Try again.")
            return False

    correct = False

    cols = st.columns(3, vertical_alignment="center")
    true_label = "True"
    if cols[0].button(label = true_label, width="stretch"):
        correct = check_answer(true_label)
    false_label = "False"
    if cols[2].button(label= false_label, width="stretch"):
        correct = check_answer(false_label)

    if correct:
        return StepOutcome(can_go_next=True)
    return StepOutcome(can_go_next=False)