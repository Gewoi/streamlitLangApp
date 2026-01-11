from __future__ import annotations

import streamlit as st
import os
from dataclasses import dataclass

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
    st.write("rendering cloze now")
    return StepOutcome(can_go_next=True)

def render_order(step: dict):
    st.write("rendering order now")
    return StepOutcome(can_go_next=True)