import streamlit as st
import langAppST.pages as pages
from langAppST.progress_handler import ProgressStore
import json
from st_cookies_manager import CookieManager


cookie_manager = CookieManager()

# Must check if cookies are ready
if not cookie_manager.ready():
    st.stop()

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
    supabase = ProgressStore()
    return supabase

if "supabase" not in st.session_state:
    st.session_state["supabase"] = connect_supabase()

def save_auth(access_token, refresh_token):
    cookie_manager["auth"] = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token
    })
    cookie_manager.save()

def get_auth():
    auth = cookie_manager.get("auth")
    if auth:
        try:
            return json.loads(auth)
        except:
            return None
    return None

def clear_auth():
    if "auth" in cookie_manager:
        del cookie_manager["auth"]
        cookie_manager.save()

if "just_logged_in" in st.session_state:
    save_auth(st.session_state.just_logged_in["access_token"], st.session_state.just_logged_in["refresh_token"])
    del st.session_state.just_logged_in

def check_session():
    auth = get_auth()
    
    if not auth or not auth.get("refresh_token"):
        st.session_state.user = None
        st.session_state.logged_in = False
        return False
    
    try:
        response = st.session_state["supabase"].supabase.auth.refresh_session(auth["refresh_token"])
        
        st.session_state.user = response.user
        st.session_state.logged_in = True
        
        save_auth(response.session.access_token, response.session.refresh_token)
        return True
    except:
        clear_auth()
        st.session_state.user = None
        st.session_state.logged_in = False
        return False

def logout():
    # Clear the auth cookie
    clear_auth()
    
    # Sign out from Supabase
    try:
        st.session_state["supabase"].supbase.auth.sign_out()
    except:
        pass
    
    st.session_state.clear()
    st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "guest" not in st.session_state:
    st.session_state.guest = False

if not st.session_state["logged_in"]:
    check_session()

if not st.session_state["logged_in"] and st.session_state["guest"]:
    result = st.session_state["supabase"].supabase.auth.sign_in_with_password({
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
    pages.course_page(nav.get("course_id"), st.session_state["supabase"])
elif page == "lesson":
    pages.player(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])
elif page == "finish":
    pages.finishing_screen(nav.get("course_id"), nav.get("current_lesson"), st.session_state["supabase"])

if page == "login":
    st.space("small")
    st.divider()
    st.link_button("Buy me a coffee", url="https://buymeacoffee.com/gewoi", icon= "☕️")
else:
    with st.sidebar.container(key="sidebar_bottom"):
        st.link_button("Support", url="https://buymeacoffee.com/gewoi", icon= "☕️")
        if logged_in:
            if st.button("Logout", type="primary", key="logout_btn"):
                logout()
