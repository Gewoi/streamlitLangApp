import streamlit as st
import langAppST.pages as pages
from langAppST.progress_handler import ProgressStore
from streamlit_supabase_auth import login_form, logout_button
from types import SimpleNamespace

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

with open('stylesheet.css') as f:
    css_file = f.read()
st.html(f"<style>{css_file}</style>")

def connect_supabase():
    return ProgressStore()

if "supabase" not in st.session_state:
    st.session_state["supabase"] = connect_supabase()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "guest" not in st.session_state:
    st.session_state["guest"] = False

# --- Restore browser session BEFORE any page renders ---
if not st.session_state["logged_in"] and not st.session_state["guest"]:
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"],
        providers=["google"],
    )
    if session:
        st.session_state["user"] = SimpleNamespace(**session["user"])
        st.session_state["logged_in"] = True
        if "nav" not in st.session_state or st.session_state["nav"].get("page") == "login":
            st.session_state["nav"] = {"page": "home"}
        st.rerun()
    # If no session found, we'll fall through to show the login page

# Guest flow
if st.session_state["guest"] and not st.session_state["logged_in"]:
    result = st.session_state["supabase"].supabase.auth.sign_in_with_password({
        "email": "guest@test.local",
        "password": "password123"
    })
    st.session_state["user"] = result.user
    st.session_state["logged_in"] = True
    st.session_state["nav"] = {"page": "home"}
    st.rerun()

if "nav" not in st.session_state:
    st.session_state["nav"] = {"page": "home"} if st.session_state["logged_in"] else {"page": "login"}

nav = st.session_state["nav"]
page = nav.get("page")

if page == "login":
    # login_form was already called above and returned None (no session),
    # so just show the guest button and extras
    st.title("Welcome!")
    st.space("small")
    st.divider()
    st.caption("Use the app as a guest. Your progress will not be saved.")
    if st.button("Continue as Guest", width="stretch"):
        st.session_state["guest"] = True
        st.rerun()
elif page == "home":
    pages.homepage()
elif page == "course_page":
    pages.course_page(nav.get("course_id"), st.session_state["supabase"])
elif page == "lesson":
    pages.player(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])
elif page == "finish":
    pages.finishing_screen(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])

if page == "login":
    st.space("small")
    st.divider()
    st.link_button("Buy me a coffee", url="https://buymeacoffee.com/gewoi", icon="☕️")
else:
    with st.sidebar.container(key="sidebar_bottom"):
        st.link_button("Support", url="https://buymeacoffee.com/gewoi", icon="☕️")
        if st.session_state["guest"]:
            if st.button("Logout", key="logout-btn", type="primary"):
                st.session_state["user"] = None
                st.session_state["guest"] = False
                st.session_state["logged_in"] = False
                st.session_state["nav"] = {"page": "login"}
                st.rerun()
        else:
            logout_button(url=st.secrets["SUPABASE_URL"], apiKey=st.secrets["SUPABASE_KEY"])