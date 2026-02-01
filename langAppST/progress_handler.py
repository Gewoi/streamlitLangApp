from __future__ import annotations

from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import streamlit as st
import random

def get_supabase_client():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

class ProgressStore:

    def __init__(self):
        self._initialize_db()

    def _initialize_db(self):
        self.supabase = get_supabase_client()
    
    def lesson_completed(self, user_id: str, course_id: str, lesson_id: str, mistakes_made : int) -> None:
        if st.session_state["guest"]:
            return 0
        
        now = datetime.now(timezone.utc).isoformat()

        self.supabase.table("lesson_progress").upsert(
            {
                "user_id": user_id,
                "course_id": course_id,
                "lesson_id": lesson_id,
                "completed": 1,
                "mistakes": mistakes_made,
                "updated_at": now,
            },
            on_conflict="user_id,course_id,lesson_id",
        ).execute()

            
    def check_lesson_completed(self, user_id: str, course_id: str, lesson_id : str):
        if st.session_state["guest"]:
            return 0

        response = (
            self.supabase.table("lesson_progress")
            .select("completed")
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .eq("lesson_id", lesson_id)
            .maybe_single()
            .execute()
        )

        if not response:
            return 0

        return int(response.data["completed"])

    def reset_lesson(self, user_id: str, course_id: str, lesson_id: str) -> None:
        if st.session_state["guest"]:
            return
        (
            self.supabase.table("lesson_progress")
            .delete()
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .eq("lesson_id", lesson_id)
            .execute()
        )

    def get_completed_lessons(self, user_id: str, course_id: str):
        """
        Returns known_words dict.
        """
        if st.session_state["guest"]:
            return []
        response = (
            self.supabase.table("lesson_progress")
            .select("lesson_id")
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .execute()
        )

        if not response:
            return []

        output = [lesson["lesson_id"] for lesson in response.data]
        return output or []

    def get_recommended_lesson(self, user_id, course_id):
        if st.session_state["guest"]:
            return None
        response = (
            self.supabase.table("lesson_progress")
            .select("lesson_id, mistakes, updated_at")
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .eq("completed", 1)
            .execute()
        )
        if not response:
            print("No lessons yet")
            return None

        # response.data contains a list of dicts
        lessons_info = response.data

        now = datetime.now(timezone.utc)

        recommended_lesson_id = ""
        prev_top_value = 0
        for lesson in lessons_info:
            
            last_done =datetime.fromisoformat(lesson["updated_at"])
            delta = now - last_done
            mistakes = lesson["mistakes"]

            MAX_MISTAKES = 12  # or 20
            norm_mistakes = min(mistakes, MAX_MISTAKES) / MAX_MISTAKES
            norm_days = delta.days / 30
            score = 0.8 * norm_mistakes + 0.2 * norm_days

            if score >= prev_top_value:
                prev_top_value = score
                recommended_lesson_id = lesson["lesson_id"]

        return recommended_lesson_id