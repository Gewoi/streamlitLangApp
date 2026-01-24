import streamlit as st
import langAppST.pages as pages
from langAppST.pages import local_storage
from langAppST.progress_handler import ProgressStore


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


@st.cache_resource
def connect_supabase():
    supabase = ProgressStore()
    return supabase

store = connect_supabase()


def check_session():
    auth = local_storage.getItem("auth")
    
    if not auth or not auth.get("refresh_token"):
        st.session_state.user = None
        st.session_state.logged_in = False
        return False
    
    try:
        from supabase import create_client
        temp_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        
        # Use refresh token to get a new session
        response = temp_client.auth.refresh_session(auth["refresh_token"])
        
        st.session_state.user = response.user
        st.session_state.logged_in = True
        
        # Update tokens
        local_storage.setItem("auth", {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        })
        return True
    except:
        local_storage.deleteItem("auth")
        st.session_state.user = None
        st.session_state.logged_in = False
        return False

def logout():
    from supabase import create_client
    temp_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    
    try:
        temp_client.auth.sign_out()
    except:
        pass
    
    local_storage.deleteItem("auth")
    st.session_state.clear()
    st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "guest" not in st.session_state:
    st.session_state.guest = False

if not st.session_state["logged_in"]:
    check_session()

if not st.session_state["logged_in"] and st.session_state["guest"]:
    result = store.supabase.auth.sign_in_with_password({
        "email": "guest@test.local",
        "password": "password123"
    })
    st.session_state["user"] = result.user
    st.session_state["session"] = result.session
    st.session_state["logged_in"] = True
    st.rerun()

logged_in = st.session_state["logged_in"]
        
if "nav" not in st.session_state:
    st.session_state["nav"] = {"page": "home"} if logged_in else {"page": "login"}
else:
    # If we just logged in (session restored) but nav is still on login page, redirect to home
    if logged_in and st.session_state["nav"].get("page") == "login":
        st.session_state["nav"] = {"page": "home"}

nav = st.session_state["nav"]

page = nav.get("page")
if page == "login":
    pages.login_page()
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
            logout()
