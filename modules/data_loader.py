import streamlit as st
import json

@st.cache_data
def load_questions():
    """Charge les questions depuis le fichier JSON"""
    try:
        with open("data/questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Fichier questions.json non trouvé. Veuillez d'abord convertir vos questions.")
        return None

@st.cache_data
def load_exam_questions():
    """Charge les questions d'examen depuis le fichier JSON"""
    try:
        with open("data/exam_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None