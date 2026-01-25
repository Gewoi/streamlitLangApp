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
    
    def lesson_completed(self, user_id: str, course_id: str, lesson_id: str, mistakes_made : int, new_words : list| None= None) -> None:
        if st.session_state["guest"]:
            return 0

        if new_words is None:
            new_words = []
        
        now = datetime.now(timezone.utc).isoformat()
        completed_list = self.get_known_words(user_id=user_id, course_id=course_id)

        #to make sure we don't add the same stuff twice
        for word in new_words:
            if word["id"] not in completed_list:
                completed_list.append(word)
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

        # ---- Upsert user_stats
        self.supabase.table("user_stats").upsert(
            {
                "user_id": user_id,
                "course_id": course_id,
                "known_words": completed_list,   # JSONB, no dumps()
            },
            on_conflict="user_id,course_id",
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

    def get_known_words(self, user_id: str, course_id: str):
        """
        Returns known_words dict.
        """
        if st.session_state["guest"]:
            return []
        response = (
            self.supabase.table("user_stats")
            .select("known_words")
            .eq("user_id", user_id)
            .eq("course_id", course_id)
            .maybe_single()
            .execute()
        )

        if not response:
            return []

        return response.data.get("known_words", []) or []

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
    
    def generate_word_repetition(self,user_id, course_id) -> dict:
        if st.session_state["guest"]:
            return None
        known_words_temp = self.get_known_words(user_id=user_id, course_id=course_id)

        number = min(len(known_words_temp), 10)


        random.shuffle(known_words_temp)
        chosen_words = known_words_temp[:number]

        lesson_dict = {"id": "REPETITION","title": "Repeat some Words!", "description": "Repeat a random selection of words", "steps" : []}

        for exercise in chosen_words:
            lesson_dict["steps"].append(exercise)
        
        return lesson_dict