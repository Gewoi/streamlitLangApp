import streamlit as st
import langAppST.pages as pages
from langAppST.progress_handler import ProgressStore
from supabase import create_client, Client

st.set_page_config(
    page_title="MyLangApp",
    page_icon="🗣",
)
css ="""
[class*="bkg_image_bern"]{
    background-image: url("https://kursaal-bern.ch/fileadmin/inhalte/Bilder/Ueber_Uns/Stories/Das-Perfekte-Wochenende-in-Bern/Kursaal-Bern_Ueber-Uns_Stories_Das-Perfekte-Wochenende-in-Bern_Zytglogge.jpg");
    background-size: 100%; 
    background-position-x: center;
    background-position-y: 60%;
    background-color: rgba(255, 255, 255, 0.8);
    background-blend-mode: lighten;
} 
[class*="finished_lesson"]{
    background: #2c9b2a;
    background: linear-gradient(90deg, rgba(44, 155, 42, 0.21) 0%, rgba(66, 189, 57, 0.41) 46%, rgba(83, 237, 147, 0.25) 100%);
}

[class*="selected_match"]{
    background: #9b8c2a;
    background: linear-gradient(153deg, rgba(155, 140, 42, 0.08) 0%, rgba(189, 189, 57, 0.15) 46%, rgba(219, 237, 83, 0.08) 100%);
}

[class*="sound_fx"]{
    display: none
}
"""

st.html(f"<style>{css}</style>")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

@st.cache_resource
def connect_supabase():
    supabase = ProgressStore()
    return supabase

store = connect_supabase()

#TODO: Take out before releasing!
if True and not st.session_state["logged_in"]:
    result = store.supabase.auth.sign_in_with_password({
        "email": "dev@test.local",
        "password": "password123"
    })
    st.session_state["user"] = result.user
    st.session_state["session"] = result.session
    st.session_state["logged_in"] = True

logged_in = st.session_state["logged_in"]

if logged_in:
    with st.sidebar:
        st.title("Settings")

nav = st.session_state.get("nav") or ({"page" : "home"} if logged_in else {"page" : "login"})

page = nav.get("page")
if page == "login":
    pages.login_page(store)
elif page == "home":
    pages.homepage()
elif page == "course_page":
    pages.course_page(nav.get("course_id"), store)
elif page == "lesson":
    pages.player(nav.get("course_id"), nav.get("current_lesson"), store)
elif page == "finish":
    pages.finishing_screen(nav.get("course_id"), nav.get("current_lesson"), store)