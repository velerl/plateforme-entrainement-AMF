import streamlit as st
import random
from datetime import datetime
from modules.config import auto_save
from modules.quiz_common import (
    render_question_header, render_question_card, render_answer_options,
    render_answer_feedback, render_navigation_buttons, render_quick_navigation,
    get_quiz_progress_info, handle_auto_positioning
)

def show_enhanced_quiz_interface():
    """Interface principale pour les quiz standards"""
    if not st.session_state.current_module:
        st.error("❌ Module non sélectionné")
        st.session_state.quiz_started = False
        st.rerun()
        return
    
    module = st.session_state.current_module
    questions = module['questions']
    
    # Vérifier et initialiser les paramètres par défaut s'ils n'existent pas
    if 'randomize_questions' not in st.session_state:
        st.session_state.randomize_questions = False
    
    # Filtrage des questions selon le mode
    if st.session_state.get('quiz_mode') == 'review':
        # Mode révision : seulement les questions incorrectes
        incorrect_questions = []
        for question in questions:
            unique_question_id = f"{module['id']}_{question['id']}"
            if unique_question_id in st.session_state.user_answers:
                user_answer = st.session_state.user_answers[unique_question_id]
                if user_answer != question['correct_answer']:
                    incorrect_questions.append(question)
        
        if not incorrect_questions:
            st.info("🎉 Aucune erreur à réviser dans ce module ! Toutes vos réponses sont correctes.")
            if st.button("🏠 Retour au menu"):
                st.session_state.quiz_started = False
                st.session_state.quiz_completed = False
                st.session_state.current_module = None
                st.rerun()
            return
        
        questions = incorrect_questions
        st.info(f"🔄 Mode révision : {len(questions)} erreur(s) à revoir")
    
    # Mélange des questions si demandé (seulement en mode practice)
    if (st.session_state.randomize_questions and 
        st.session_state.get('quiz_mode') == 'practice' and 
        'shuffled_questions' not in st.session_state):
        st.session_state.shuffled_questions = questions.copy()
        random.shuffle(st.session_state.shuffled_questions)
    
    if (st.session_state.randomize_questions and 
        st.session_state.get('quiz_mode') == 'practice'):
        questions = st.session_state.shuffled_questions
    
    # Positionnement automatique
    handle_auto_positioning(questions, module['id'])
    
    current_idx = st.session_state.current_question_idx
    
    if current_idx >= len(questions):
        st.session_state.quiz_completed = True
        st.rerun()
        return
    
    current_question = questions[current_idx]
    
    # En-tête du quiz avec indication du mode
    mode_emoji = {
        'practice': '🎯',
        'review': '🔄'
    }.get(st.session_state.get('quiz_mode', 'practice'), '📝')
    
    title = f"{mode_emoji} Thème {module['id']} : {module['full_title']}"
    render_question_header(title)
    
    # Barre de progression
    if st.session_state.get('quiz_mode') == 'review':
        # En mode révision, progression basée sur les questions revues
        answered_questions = sum(1 for i, q in enumerate(questions) if i <= current_idx)
        progress = answered_questions / len(questions)
    else:
        # En mode practice, progression basée sur toutes les questions du module
        all_questions = module['questions']
        answered_questions = sum(1 for q in all_questions if f"{module['id']}_{q['id']}" in st.session_state.user_answers)
        progress = answered_questions / len(all_questions)
    
    st.progress(progress)
    
    # Affichage de la question
    render_question_card(current_question['id'], current_question['question'])
    
    # Options de réponse
    unique_question_id = f"{module['id']}_{current_question['id']}"
    radio_key = f"q_{current_question['id']}_{st.session_state.get('quiz_mode', 'practice')}"
    user_choice = render_answer_options(current_question['options'], unique_question_id, radio_key)
    
    # Stocker le choix actuel pour les boutons
    st.session_state.current_user_choice = user_choice
    
    # Afficher les réponses correctes/incorrectes si déjà répondu (UNE SEULE FOIS)
    if unique_question_id in st.session_state.user_answers:
        user_answer = st.session_state.user_answers[unique_question_id]
        correct_answer = current_question['correct_answer']
        options = current_question['options']
        
        if user_answer == correct_answer:
            st.success(f"✅ **Correct !** Votre choix : {user_answer} - {options[user_answer]}")
        else:
            st.error(f"❌ **Incorrect** • Votre choix : {user_answer} - {options[user_answer]}")
            st.info(f"🎯 **Bonne réponse :** {correct_answer} - {options[correct_answer]}")
    
    # Feedback immédiat (seulement pour les examens blancs)
    is_exam_mode = st.session_state.get('quiz_mode') == 'exam_blanc'
    render_answer_feedback(unique_question_id, show_saved_message=is_exam_mode)
    
    
    # Boutons de navigation
    render_navigation_buttons(
        current_idx=current_idx,
        total_questions=len(questions),
        unique_question_id=unique_question_id,
        auto_save_func=auto_save
    )
    
    # Navigation rapide
    render_quick_navigation(
        questions=questions,
        current_idx=current_idx,
        module_id=module['id'],
        title_suffix=f"{len(questions)} questions"
    )