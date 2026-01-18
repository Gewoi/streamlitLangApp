from __future__ import annotations

import streamlit as st
import streamlit_extras as ste
import os
from dataclasses import dataclass
import pathlib as Path
from string import ascii_letters
from .content import resize_image, play_correct, play_wrong, play_match_correct

import random

@dataclass
class StepOutcome:
    can_go_next: bool

def comparison_string(input_string : str):
    result = ''.join([letter for letter in input_string if letter in ascii_letters])
    result = result.casefold()
    return result

def mistake_made():
    st.session_state["mistakes"] += 1
    play_wrong()

def render_step(step : dict):
    stype = str(step.get("type", "markdown"))
    if stype == "markdown":
        return render_markdown(step)
    if stype == "introduce_word":
        return render_introduce_word(step)
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

@st.fragment
def render_markdown(step : dict):
    st.markdown(step.get("markdown", "no markdown found"), unsafe_allow_html=True)

    images = step.get("images", [])
    audio = step.get("audio", None)
    for img in images or []:
        with st.container(horizontal_alignment="center"):
            for img in images:
                if os.path.exists(img):
                    st.image(resize_image(img))

    if audio:
        if os.path.exists(audio):
            st.audio(audio, autoplay=True)
        else:
            st.info(f"(Missing audio asset: {audio})")

    return StepOutcome(can_go_next=True)

@st.fragment
def render_introduce_word(step : dict):
    word = step["word"]

    original = step["translation"]["en"] or None
    helper = step["translation"]["de"] or None

    images = step.get("images", [])
    audio = step["audio"]

    for img in images or []:
        with st.container(horizontal_alignment="center"):
            for img in images:
                if os.path.exists(img):
                    st.image(resize_image(img))

    
    if audio:
        if os.path.exists(audio):
            st.audio(audio, autoplay=True)
        else:
            st.info(f"(Missing audio asset: {audio})")

    st.subheader(word, text_alignment="center")
    if original:
        st.markdown(original, text_alignment="center")
    if helper:
        st.caption(helper, text_alignment="center")

    return StepOutcome(can_go_next=True)


@st.fragment
def render_cloze(step: dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data.get("question", None)
    goal_sentence_arr = sentence_data["target"]
    helper_sentence = sentence_data.get("helper", None)

    sol_display = step.get("solution_display", None)
    
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
            with st.container(horizontal_alignment="center"):
                for img in images:
                    if os.path.exists(img):
                        st.image(resize_image(img))
        if audio:
            if os.path.exists(audio):
                st.audio(audio, autoplay=True)
            else:
                st.info(f"(Missing audio asset: {audio})")
        
        st.space("small")

        if st.session_state["take_over_answer"] == "":
            blank_space = ""
            for i in range(len(solutions[0])):
                blank_space += "_"
                
            full_question_sentence = str(goal_sentence_arr[0] + blank_space + goal_sentence_arr[1])
            st.markdown(f"### {full_question_sentence}", text_alignment="center")
        else:
            st.markdown(f"### {st.session_state["take_over_answer"]}", text_alignment="center")

        answer = st.text_input("answer_cloze", autocomplete="off", label_visibility="hidden", value="")
        submitted = st.form_submit_button("Check", width="stretch")


    #st.space("small")
    if submitted:
        if comparison_string(answer) in caseIns_solutions:
            st.session_state["take_over_answer"] = str(goal_sentence_arr[0] + answer + goal_sentence_arr[1])
            st.rerun()
        else:
            mistake_made()
            st.error("Not quite. Try again.")

    if not st.session_state["take_over_answer"] == "":
        if sol_display:
            st.success(sol_display)
        else:
            st.success("Correct ✅")
        play_correct()
        st.session_state["take_over_answer"] =  ""
        return StepOutcome(can_go_next=True)

    return StepOutcome(can_go_next=False)

@st.fragment
def render_order(step: dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data.get("question", None)
    helper_sentence = sentence_data.get("helper", None)
    if st.session_state["order_tokens"] == []:
        st.session_state["correct_order"] = list(step["tokens"])
        tokens = list(step["tokens"])
        random.shuffle(tokens)
        st.session_state["order_tokens"] = list(tokens)
        used_tokens = []
    else:
        tokens = list(st.session_state["order_tokens"])
        used_tokens = list(st.session_state["used_tokens"])

    solutions = st.session_state["correct_order"]

    audio = step.get("audio", None)
    images = step.get("images", None)

    sol_display = step.get("solution_display", None)


    if original_sentence:
        st.markdown(f"__{original_sentence}__", text_alignment="center")
    if helper_sentence:
        st.caption(helper_sentence, text_alignment="center")
    if images:
        with st.container(horizontal_alignment="center"):
            for img in images:
                if os.path.exists(img):
                    st.image(resize_image(img))
    if audio:
        if os.path.exists(audio):
            st.audio(audio, autoplay=True)
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
        submitted = st.form_submit_button("Check", width="stretch", shortcut="enter")

    if submitted:
        if st.session_state["order_answer"] == solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            play_correct()
            return StepOutcome(can_go_next=True)
        else:
            mistake_made()
            st.error("Not quite. Try again.")
    return StepOutcome(can_go_next=False)

@st.fragment
def render_translate_type(step : dict):
    sentence_data = step["sentence"]
    original_sentence = sentence_data.get("question", None)
    helper_sentence = sentence_data.get("helper", None)

    sol_display = step.get("solution_display", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(comparison_string(sol))

    audio = step.get("audio", None)
    images = step.get("images", None)

    #st.space("small")
    with st.form("answer", border=False):
        if original_sentence:
            st.markdown(f"### {original_sentence}", text_alignment="center")
        if helper_sentence:
            st.caption(helper_sentence, text_alignment="center")
        if images:
            with st.container(horizontal_alignment="center"):
                for img in images:
                    if os.path.exists(img):
                        st.image(resize_image(img))
        if audio:
            if os.path.exists(audio):
                st.audio(audio, autoplay=True)
            else:
                st.info(f"(Missing audio asset: {audio})")

        answer_type = st.text_input("answer_type", label_visibility="hidden", autocomplete="off", value = "")
        
        submitted = st.form_submit_button("Check", width="stretch")
    
    if submitted:
        if comparison_string(answer_type) in caseIns_solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            play_correct()
            return StepOutcome(can_go_next=True)
        else:
            mistake_made()
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)


@st.fragment
def render_listen_type(step : dict):
    sol_display = step.get("solution_display", None)
    
    solutions = step["answers"]
    caseIns_solutions = []
    for sol in solutions:
        caseIns_solutions.append(comparison_string(sol))

    audio = step["audio"]
    images = step.get("images", None)

    #st.space("small")
    with st.form("answer", border=False):
        if images:
            with st.container(horizontal_alignment="center"):
                for img in images:
                    if os.path.exists(img):
                        st.image(resize_image(img))
        if os.path.exists(audio):
            st.audio(audio, autoplay=True)
        else:
            st.info(f"(Missing audio asset: {audio})")

        answer_listen = st.text_input("answer_listen", label_visibility="hidden", autocomplete="off", value = "")
        
        submitted = st.form_submit_button("Check", width="stretch")
    
    if submitted:
        if comparison_string(answer_listen) in caseIns_solutions:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            play_correct()
            return StepOutcome(can_go_next=True)
        else:
            mistake_made()
            st.error("Not quite. Try again.")

    return StepOutcome(can_go_next=False)

@st.fragment
def render_match(step : dict):
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
    
    def give_css_selected(elm, lang : str):
        if elm[lang] in st.session_state["last_pair"]:
            key = f"order_button_sel_{elm[lang]}"
        else:
            key = f"selected_match_{elm[lang]}" if elm[lang] == match_sel_btn else elm[lang]
        return key

    def check_buttons(elm, lang : str):
        if match_sel_btn:
            if elm[lang] == corresponding_btn:
                st.session_state["pressed_match_buttons"] += [elm[lang], match_sel_btn]
                st.session_state["match_sel_btn"] = None
                play_match_correct()
                st.session_state["last_pair"] = [corresponding_btn, match_sel_btn]
                st.rerun()
            else:
                st.session_state["match_sel_btn"] = None
                play_wrong()
                st.rerun()
        else:
            st.session_state["last_pair"] = []
            st.session_state["match_sel_btn"] = elm[lang]
            st.rerun()

    cols = st.columns([2,1,2], gap="medium")
    for elm in left:
        disable_cond = elm["original"] in pressed_match_btns or elm["original"] == match_sel_btn
        if cols[0].button(label =elm["original"], width="stretch", disabled=disable_cond, key = give_css_selected(elm, "original")):
            check_buttons(elm, "original")
    for elm in right:
        disable_cond = elm["target"] in pressed_match_btns or elm["target"] == match_sel_btn
        if cols[2].button(label =elm["target"], width="stretch", disabled=disable_cond, key = give_css_selected(elm, "target")):
            check_buttons(elm, "target")

    if len(st.session_state["pressed_match_buttons"]) == len(all_buttons):
        st.success("Correct ✅")
        play_correct()
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
            st.audio(audio, autoplay=True)
        else:
            st.info(f"(Missing audio asset: {audio})")
    if images:
        with st.container(horizontal_alignment="center"):
            for img in images:
                if os.path.exists(img):
                    st.image(resize_image(img))
    
    st.space("medium")
    st.markdown(f"### {display_text}", text_alignment="center")

    def check_answer(label):
        if answer == label:
            if sol_display:
                st.success(sol_display)
            else:
                st.success("Correct ✅")
            play_correct()
            return True
        else:
            mistake_made()
            st.error("Not quite. Try again.")
            return False

    correct = False
    st.space("small")
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