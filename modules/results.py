import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from modules.utils import calculate_score, get_performance_level

def show_enhanced_results():
    """Affiche les résultats détaillés du quiz"""
    if not st.session_state.current_module:
        return
    
    module = st.session_state.current_module
    questions = st.session_state.get('shuffled_questions', module['questions'])
    
    # Calcul des résultats détaillés
    correct, total = calculate_score(questions, st.session_state.user_answers, module['id'])
    score_percentage = (correct / total) * 100 if total > 0 else 0
    level, level_type = get_performance_level(score_percentage)
    
    # En-tête des résultats
    st.markdown(f"""
    <div class="results-header">
        <h1>🎉 Quiz terminé !</h1>
        <h2>📝 {module['title']} - {module['description']}</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem;">{level}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques des résultats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: var(--success-color);">✅</h3>
            <h2 style="color: var(--success-color);">{correct}</h2>
            <p>Bonnes réponses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: var(--danger-color);">❌</h3>
            <h2 style="color: var(--danger-color);">{total - correct}</h2>
            <p>Erreurs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: var(--primary-color);">📊</h3>
            <h2 style="color: var(--primary-color);">{score_percentage:.1f}%</h2>
            <p>Score final</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.start_time:
            duration = datetime.now() - st.session_state.start_time
            minutes = duration.seconds // 60
            seconds = duration.seconds % 60
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: var(--info-color);">⏱️</h3>
                <h2 style="color: var(--info-color);">{minutes}m {seconds}s</h2>
                <p>Temps total</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        avg_time = (datetime.now() - st.session_state.start_time).seconds / total if st.session_state.start_time and total > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: var(--warning-color);">⚡</h3>
            <h2 style="color: var(--warning-color);">{avg_time:.0f}s</h2>
            <p>Temps/question</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Analyse détaillée
    st.subheader("📈 Analyse détaillée")
    
    if score_percentage >= 80:
        st.success(f"🎉 Excellente performance ! Vous maîtrisez bien ce module avec {score_percentage:.1f}%.")
    elif score_percentage >= 60:
        st.info(f"👍 Bonne performance ! Vous avez obtenu {score_percentage:.1f}%. Quelques révisions pourraient vous aider à atteindre l'excellence.")
    else:
        st.warning(f"📚 Il y a encore du travail ! Avec {score_percentage:.1f}%, une révision approfondie de ce module serait bénéfique.")
    
    # Boutons d'action
    st.subheader("🎯 Que souhaitez-vous faire maintenant ?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Recommencer ce module", type="primary", use_container_width=True):
            # Nettoyer les réponses de ce module
            questions_ids = [f"{module['id']}_{q['id']}" for q in questions]
            for q_id in questions_ids:
                if q_id in st.session_state.user_answers:
                    del st.session_state.user_answers[q_id]
            
            # Sauvegarder les changements
            from modules.persistence import save_user_progress
            save_user_progress(force_save=True)
            
            # Redémarrer le quiz directement
            st.session_state.current_question_idx = 0
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.start_time = datetime.now()
            if 'shuffled_questions' in st.session_state:
                del st.session_state.shuffled_questions
            st.rerun()
    
    with col2:
        if st.button("📚 Tableau de bord", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.current_module = None
            if 'shuffled_questions' in st.session_state:
                del st.session_state.shuffled_questions
            st.rerun()
    
    # Vérifier s'il y a des erreurs
    errors = [q for q in questions if f"{module['id']}_{q['id']}" in st.session_state.user_answers and 
              st.session_state.user_answers[f"{module['id']}_{q['id']}"] != q['correct_answer']]
    
    # Affichage conditionnel selon l'état
    if not st.session_state.get('show_error_review', False):
        # Affichage normal des boutons
        with col3:
            if errors and st.button("📝 Revoir les erreurs", use_container_width=True):
                # Afficher la révision des erreurs sur toute la largeur
                st.session_state.show_error_review = True
                st.rerun()
    else:
        # Affichage de la révision des erreurs sur toute la largeur
        if st.button("🏠 Retour aux résultats", type="secondary"):
            st.session_state.show_error_review = False
            st.rerun()
        
        show_enhanced_error_review(errors)

def show_enhanced_error_review(errors):
    """Affiche la révision détaillée des erreurs"""
    st.subheader("🔍 Révision détaillée des erreurs")
    
    if not errors:
        st.success("🎉 Aucune erreur à réviser ! Parfait !")
        return
    
    # Récupérer le module actuel pour les identifiants uniques
    module = st.session_state.current_module
    
    st.info(f"📋 Vous avez fait {len(errors)} erreur(s). Prenez le temps de bien comprendre ces questions.")
    
    for i, question in enumerate(errors):
        with st.expander(f"❌ Question {question['id']} - Erreur {i+1}/{len(errors)}", expanded=i==0):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                unique_q_id = f"{module['id']}_{question['id']}"
                user_answer = st.session_state.user_answers[unique_q_id]
                
                # Question
                st.markdown("**Question**")
                st.write(question['question'])
                
                # Votre réponse (incorrecte)
                st.markdown("**❌ Votre réponse**")
                st.error(f"**{user_answer}** - {question['options'][user_answer]}")
                
                # Bonne réponse
                st.markdown("**✅ Bonne réponse**")
                st.success(f"**{question['correct_answer']}** - {question['options'][question['correct_answer']]}")
            
            with col2:
                # Bouton pour marquer comme comprise
                if st.button(f"✅ Compris", key=f"understood_{question['id']}"):
                    st.success("👍 Question marquée comme comprise !")