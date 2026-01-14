import streamlit as st
import langAppST.pages as pages

st.set_page_config(
    page_title="MyLangApp",
    page_icon="🗣"
)

nav = st.session_state.get("nav") or {"page" : "home"}

page = nav.get("page")
if page == "home":
    pages.homepage()
elif page == "course_page":
    pages.course_page(nav.get("course_id"))
elif page == "lesson":
    pages.player(nav.get("course_id"), nav.get("current_lesson"))
elif page == "finish":
    pages.finishing_screen(nav.get("course_id"), nav.get("current_lesson"))

with st.sidebar:
    st.title("This is a sidebar")