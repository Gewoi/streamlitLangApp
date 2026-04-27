import streamlit as st
import langAppST.pages as pages
from langAppST.progress_handler import ProgressStore
from streamlit_supabase_auth import login_form, logout_button
from types import SimpleNamespace
import base64
import pathlib as Path

if st.session_state.get("logged_in", False) and not st.session_state.get("guest", True):
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"],
        providers=["google"],
    )
    if not session:
        # Browser session was cleared (user logged out)
        st.session_state["user"] = None
        st.session_state["logged_in"] = False
        st.session_state["guest"] = False
        st.session_state["nav"] = {"page": "login"}
        st.rerun()

st.set_page_config(
    page_title="LangApp",
    page_icon="🗣",
    initial_sidebar_state="auto"
)

st.html('''
       <script>
        window.top.document.querySelectorAll(`[href*="streamlit.io"]`).forEach(e => e.setAttribute("style", "display: none;"));
      </script>
    ''')

@st.cache_data
def load_styled_css():
    with open('stylesheet.css') as f:
        css = f.read()
    img_b64 = base64.b64encode(Path.Path('data/assets/images/bern.jpg').read_bytes()).decode()
    return css.replace(
        "url('data/assets/images/bern.jpg')",
        f"url('data:image/jpeg;base64,{img_b64}')"
    )

css_file = load_styled_css()

st.html(f"<style>{css_file}</style>")

def connect_supabase():
    supabase = ProgressStore()
    return supabase

if "supabase" not in st.session_state:
    st.session_state["supabase"] = connect_supabase()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "guest" not in st.session_state:
    st.session_state["guest"] = False

# Guest flow stays the same
if st.session_state["guest"] and not st.session_state["logged_in"]:
    st.session_state["user"] = SimpleNamespace(id=None, email=None)
    st.session_state["logged_in"] = True
    st.session_state["nav"] ={"page": "home"}
    st.rerun()

        
if "nav" not in st.session_state:
    if st.session_state["logged_in"]:
        st.session_state["nav"] ={"page": "home"}
    else:
        st.session_state["nav"] ={"page": "login"}

nav = st.session_state["nav"]

page = nav.get("page")
if page == "login":
    pages.login_page()
elif page == "home" and st.session_state["logged_in"]:
    pages.homepage()
elif page == "course_page" and st.session_state["logged_in"]:
    pages.course_page(nav.get("course_id"), st.session_state["supabase"])
elif page == "lesson" and st.session_state["logged_in"]:
    pages.player(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])
elif page == "finish" and st.session_state["logged_in"]:
    pages.finishing_screen(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])

if page == "login":
    st.space("small")
    st.divider()
    st.link_button("Buy me a coffee", url="https://buymeacoffee.com/gewoi", icon= "☕️")
else:
    with st.sidebar.container(key="sidebar_bottom"):
        st.link_button("Support", url="https://buymeacoffee.com/gewoi", icon= "☕️")
        if st.session_state["guest"]:
            if st.button("Logout", key="logout-btn", type="primary"):
                st.session_state["user"] = None
                st.session_state["guest"] = False
                st.session_state["logged_in"] = False
                st.session_state["nav"] = {"page": "login"}
                st.rerun()
        else:
            logout_button(url=st.secrets["SUPABASE_URL"], apiKey=st.secrets["SUPABASE_KEY"])
