import streamlit as st
import langAppST.pages as pages
from langAppST.progress_handler import ProgressStore
from supabase import create_client, Client
from streamlit_extras.bottom_container import bottom

st.set_page_config(
    page_title="MyLangApp",
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


@st.cache_resource
def connect_supabase():
    supabase = ProgressStore()
    return supabase

store = connect_supabase()

def restore_session():
    if "supabase_session" in st.session_state:
        store.supabase.auth.set_session(
            st.session_state["supabase_session"]["access_token"],
            st.session_state["supabase_session"]["refresh_token"],
        )

        user = store.supabase.auth.get_user()
        if user:
            st.session_state["user"] = user.user
            st.session_state["logged_in"] = True
            return True

    return False

def logout(supabase : ProgressStore):
    supabase.supabase.auth.sign_out()
    st.session_state.clear()
    st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = restore_session()

if "guest" not in st.session_state:
    st.session_state.guest = False

if "user" not in st.session_state:
    st.session_state.user = None



if not st.session_state["logged_in"] and st.session_state["guest"]:
    result = store.supabase.auth.sign_in_with_password({
        "email": "guest@test.local",
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


with st.sidebar.container(key="sidebar_bottom"):
    st.link_button("Support", url="https://buymeacoffee.com/gewoi", icon= "☕️")
    if logged_in:
        if st.button("Logout", type="primary", key="logout_btn"):
            logout(store)
