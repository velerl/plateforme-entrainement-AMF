import streamlit as st
from datetime import datetime
import json
import random

# Imports des modules
from modules.config import inject_custom_css, initialize_session_state
from modules.data_loader import load_questions, load_exam_questions
from modules.dashboard import show_enhanced_dashboard
from modules.quiz_interface import show_enhanced_quiz_interface
from modules.exam_blanc import show_exam_blanc_interface, show_exam_blanc_results, create_exam_blanc, show_exam_blanc_review_interface
from modules.results import show_enhanced_results
from modules.utils import get_user_progress, calculate_score

# Import du nouveau système de persistance
from modules.persistence import (
    initialize_session_with_persistence, 
    save_user_progress, 
    show_progress_info,
    on_answer_validated,
    reset_user_progress,
    test_directory_creation
)

# Configuration de la page
st.set_page_config(
    page_title="Entraînement AMF",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    inject_custom_css()
    initialize_session_state()
    
    # Système de persistance : ne charger qu'une seule fois par session
    if 'persistence_initialized' not in st.session_state:
        initialize_session_with_persistence()
        st.session_state.persistence_initialized = True
    
    data = load_questions()
    
    if not data:
        return
    
    # En-tête amélioré (seulement si pas dans un quiz)
    if not st.session_state.quiz_started:
        st.markdown("""
        <div class="main-header pulse-animation">
            <h1>🧠 Entraînement AMF</h1>
            <p>Maîtrisez vos connaissances avec 560 questions réparties en 12 modules</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar simplifiée (seulement si pas dans un quiz actif)
    if not st.session_state.quiz_started or st.session_state.quiz_completed:
        with st.sidebar:
            st.title("📚 Navigation")
            
            # Bouton retour au menu si on est sur la page de résultats
            if st.session_state.quiz_completed:
                if st.button("🏠 Retour au menu", type="primary", use_container_width=True):
                    # Sauvegarder avant de quitter
                    save_user_progress()
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_module = None
                    st.session_state.exam_blanc_questions = None
                    st.session_state.exam_blanc_part = 1
                    if 'exam_blanc_review_questions' in st.session_state:
                        del st.session_state.exam_blanc_review_questions
                    if 'shuffled_questions' in st.session_state:
                        del st.session_state.shuffled_questions
                    if 'show_error_review' in st.session_state:
                        del st.session_state.show_error_review
                    st.rerun()
                
                st.divider()
            
            # Sauvegarde automatique uniquement
            st.markdown("""
            <div class="stats-card">
                <h4>💾 Sauvegarde Auto</h4>
            </div>
            """, unsafe_allow_html=True)

            # Sélection du module
            st.subheader("🎯 Choisir un module")
            module_options = [f"{m['title']} - {m['full_title']}" for m in data['modules']]
            selected_module_idx = st.selectbox(
                "Sélectionner un module", 
                range(len(module_options)), 
                format_func=lambda i: module_options[i],
                label_visibility="collapsed"
            )

            current_module = data['modules'][selected_module_idx]
            
            # Statistiques du module sélectionné
            correct, total_answered = calculate_score(current_module['questions'], st.session_state.user_answers, current_module['id'])
            if total_answered > 0:
                module_score = (correct / total_answered) * 100
                from modules.utils import get_performance_level
                level, level_type = get_performance_level(module_score)
                
                st.markdown(f"""
                <div class="module-card">
                    <h4>📈 Performance du module</h4>
                    <p><strong>Score:</strong> {module_score:.1f}%</p>
                    <p><strong>Niveau:</strong> {level}</p>
                    <p><strong>Questions:</strong> {total_answered}/{current_module['total_questions']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Bouton Révision des erreurs (sans titre)
            if st.button("❌ Réviser les erreurs", type="secondary", use_container_width=True):
                st.session_state.current_module = current_module
                st.session_state.current_question_idx = 0
                st.session_state.quiz_started = True
                st.session_state.quiz_completed = False
                st.session_state.start_time = datetime.now()
                st.session_state.quiz_mode = 'review'
                # Nettoyer les données d'examen blanc
                st.session_state.exam_blanc_questions = None
                st.session_state.current_exam_blanc_id = None
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)  # Petit espace

            # Bouton de reset (sans titre)
            if st.button("🔄 Réinitialiser toute la progression", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_reset', False):
                    if reset_user_progress():
                        st.success("✅ Progression réinitialisée et sauvegardée dans checkpoint/")
                    else:
                        st.error("❌ Erreur lors de la réinitialisation")
                    st.session_state.confirm_reset = False
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer la réinitialisation complète")
    
    # Sidebar simplifiée pendant le quiz
    elif st.session_state.quiz_started:
        with st.sidebar:
            if st.session_state.quiz_mode == 'exam_blanc':
                # Affichage du numéro d'examen dans le titre
                exam_id = st.session_state.get('current_exam_blanc_id', '???')
                st.title(f"🎓 Examen Blanc #{exam_id}")
                
                # Bouton de retour principal
                if st.button("🏠 Retour au menu", type="primary", use_container_width=True):
                    # Sauvegarder avant de quitter
                    save_user_progress()
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_module = None
                    st.session_state.exam_blanc_questions = None
                    st.session_state.exam_blanc_part = 1
                    if 'exam_blanc_review_questions' in st.session_state:
                        del st.session_state.exam_blanc_review_questions
                    if 'shuffled_questions' in st.session_state:
                        del st.session_state.shuffled_questions
                    st.rerun()
                
                st.divider()
                
                # Progression de l'examen blanc
                if st.session_state.exam_blanc_questions:
                    exam_data = st.session_state.exam_blanc_questions
                    
                    # Calculer la progression
                    part1_answered = sum(1 for q in exam_data['part1']['questions'] 
                                       if q['id'] in st.session_state.user_answers)
                    part2_answered = sum(1 for q in exam_data['part2']['questions'] 
                                       if q['id'] in st.session_state.user_answers)
                    total_answered = part1_answered + part2_answered
                    total_questions = exam_data['total_questions']
                    
                    # Temps écoulé
                    if st.session_state.start_time:
                        elapsed = datetime.now() - st.session_state.start_time
                        elapsed_minutes = int(elapsed.total_seconds() / 60)
                        elapsed_hours = elapsed_minutes // 60
                        elapsed_mins = elapsed_minutes % 60
                        
                        # Indicateur de couleur selon le temps
                        if elapsed_minutes > 120:  # Plus de 2h
                            time_color = 'var(--danger-color)'
                            time_icon = '🔴'
                        elif elapsed_minutes > 90:  # Plus de 1h30
                            time_color = 'var(--warning-color)'
                            time_icon = '🟡'
                        else:
                            time_color = 'var(--success-color)'
                            time_icon = '🟢'
                    
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>📊 Progression Examen</h3>
                        <p><strong>Partie {st.session_state.exam_blanc_part}</strong> / 2</p>
                        <p>Complétées: <strong>{total_answered}</strong> / {total_questions}</p>
                        <p>Partie 1: {part1_answered} / {len(exam_data['part1']['questions'])}</p>
                        <p>Partie 2: {part2_answered} / {len(exam_data['part2']['questions'])}</p>
                        <p style="color: {time_color};">{time_icon} {elapsed_hours}h{elapsed_mins:02d}m</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Indication de temps
                    if elapsed_minutes > 120:
                        st.warning("⏰ Temps indicatif dépassé (2h)")
                    
                    st.info("**Mode:** 🎓 Examen blanc")
                    
                    st.divider()
                    
                    # Bouton de réinitialisation de l'examen blanc
                    if st.button(f"🗑️ Réinitialiser Examen #{exam_id}", 
                               type="secondary", 
                               use_container_width=True,
                               help=f"Supprimer toutes les réponses de l'examen #{exam_id}"):
                        if st.session_state.get(f'confirm_reset_exam_{exam_id}', False):
                            # Supprimer toutes les réponses de cet examen
                            keys_to_remove = []
                            for key in st.session_state.user_answers.keys():
                                if key.startswith(f'exam{exam_id}_'):
                                    keys_to_remove.append(key)
                            
                            for key in keys_to_remove:
                                del st.session_state.user_answers[key]
                            
                            # Sauvegarder les changements
                            save_user_progress(force_save=True)
                            
                            # Rester sur l'examen mais revenir à la première question
                            st.session_state.current_question_idx = 0
                            st.session_state.exam_blanc_part = 1
                            
                            st.session_state[f'confirm_reset_exam_{exam_id}'] = False
                            st.success(f"✅ Examen #{exam_id} réinitialisé!")
                            st.rerun()
                        else:
                            st.session_state[f'confirm_reset_exam_{exam_id}'] = True
                            st.warning(f"⚠️ Supprimer toutes les réponses de l'examen #{exam_id} ? Cliquez à nouveau pour confirmer.")
            
            elif st.session_state.quiz_mode == 'exam_blanc_review':
                # Sidebar pour la révision d'examen blanc
                exam_id = st.session_state.get('current_exam_blanc_id', '???')
                st.title(f"🔄 Révision Examen #{exam_id}")
                
                # Bouton de retour principal
                if st.button("🏠 Retour au menu", type="primary", use_container_width=True):
                    # Sauvegarder avant de quitter
                    save_user_progress()
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_module = None
                    st.session_state.exam_blanc_questions = None
                    st.session_state.exam_blanc_part = 1
                    if 'exam_blanc_review_questions' in st.session_state:
                        del st.session_state.exam_blanc_review_questions
                    st.rerun()
                
                st.divider()
                
                # Progression de la révision
                if 'exam_blanc_review_questions' in st.session_state:
                    review_questions = st.session_state.exam_blanc_review_questions
                    current_idx = st.session_state.current_question_idx
                    
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>🔄 Révision Erreurs</h3>
                        <p><strong>Question {current_idx + 1}</strong> / {len(review_questions)}</p>
                        <p>Erreurs à revoir: <strong>{len(review_questions)}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info("**Mode:** 🔄 Révision des erreurs")
                    
            else:
                st.title("📝 Quiz en cours")
                
                # Bouton de retour principal
                if st.button("🏠 Retour au menu", type="primary", use_container_width=True):
                    # Sauvegarder avant de quitter
                    save_user_progress()
                    st.session_state.quiz_started = False
                    st.session_state.quiz_completed = False
                    st.session_state.current_module = None
                    if 'shuffled_questions' in st.session_state:
                        del st.session_state.shuffled_questions
                    st.rerun()
                
                st.divider()
                
                # Progression du quiz normal
                if st.session_state.current_module:
                    module = st.session_state.current_module
                    questions = st.session_state.get('shuffled_questions', module['questions'])
                    current_idx = st.session_state.current_question_idx
                    total_questions = len(questions)
                    
                    # Calculer les questions répondues
                    answered_questions = sum(1 for q in questions if f"{module['id']}_{q['id']}" in st.session_state.user_answers)
                    progress = answered_questions / total_questions
                    
                    st.markdown(f"""
                    <div class="stats-card">
                        <h3>📊 Progression</h3>
                        <p><strong>{answered_questions}</strong> / {total_questions} complétées</p>
                        <p><strong>{progress:.1%}</strong> complété</p>
                        <p style="font-size: 0.9em; opacity: 0.8;">Question actuelle: {current_idx + 1}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mode actuel
                    mode_text = {
                        'practice': '🎯 Entraînement',
                        'review': '🔄 Révision'
                    }.get(st.session_state.quiz_mode, 'Mode inconnu')
                    
                    st.info(f"**Mode actuel:** {mode_text}")

                    st.divider()

                    # Bouton de réinitialisation du module
                    if st.button(f"🗑️ Réinitialiser {module['title']}", 
                               type="secondary", 
                               use_container_width=True,
                               help=f"Supprimer toutes les réponses du {module['title']}"):
                        if st.session_state.get(f'confirm_reset_module_{module["id"]}', False):
                            # Supprimer toutes les réponses de ce module
                            keys_to_remove = []
                            for key in st.session_state.user_answers.keys():
                                if key.startswith(f"{module['id']}_"):
                                    keys_to_remove.append(key)
                            
                            for key in keys_to_remove:
                                del st.session_state.user_answers[key]
                            
                            # Sauvegarder les changements
                            save_user_progress(force_save=True)
                            
                            # Rester sur le quiz mais revenir à la première question
                            st.session_state.current_question_idx = 0
                            if 'shuffled_questions' in st.session_state:
                                del st.session_state.shuffled_questions
                            
                            st.session_state[f'confirm_reset_module_{module["id"]}'] = False
                            st.success(f"✅ {module['title']} réinitialisé!")
                            st.rerun()
                        else:
                            st.session_state[f'confirm_reset_module_{module["id"]}'] = True
                            st.warning(f"⚠️ Supprimer toutes les réponses du {module['title']} ? Cliquez à nouveau pour confirmer.")
    
    # Contenu principal
    if not st.session_state.quiz_started:
        show_enhanced_dashboard(data)
    elif st.session_state.quiz_completed:
        if st.session_state.quiz_mode == 'exam_blanc':
            show_exam_blanc_results()
        elif st.session_state.quiz_mode == 'exam_blanc_review':
            # Fin de révision d'examen blanc, retourner aux résultats
            st.session_state.quiz_mode = 'exam_blanc'
            st.session_state.quiz_completed = True
            show_exam_blanc_results()
        else:
            show_enhanced_results()
    else:
        if st.session_state.quiz_mode == 'exam_blanc':
            show_exam_blanc_interface()
        elif st.session_state.quiz_mode == 'exam_blanc_review':
            show_exam_blanc_review_interface()
        else:
            show_enhanced_quiz_interface()

if __name__ == "__main__":
    main()