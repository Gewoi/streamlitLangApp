import streamlit as st
import base64
import html

def audio_no_download(file_path, autoplay=False, key=""):
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    
    ext = file_path.split(".")[-1]
    mime = {"mp3": "audio/mpeg", "wav": "audio/wav", "ogg": "audio/ogg"}.get(ext, "audio/mpeg")
    
    autoplay_attr = "autoplay" if autoplay else ""
    safe_key = html.escape(key, quote=True)
    
    st.html(
        f'<audio id="{safe_key}" controls controlsList="nodownload" {autoplay_attr} style="width: 100%;">'
        f'<source src="data:{mime};base64,{data}" type="{mime}">'
        f'</audio>'
    )