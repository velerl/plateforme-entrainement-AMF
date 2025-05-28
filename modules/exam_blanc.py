import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.data_loader import load_exam_questions
from modules.config import auto_save
from modules.quiz_common import (
    render_question_header, render_question_card, render_answer_options,
    render_answer_feedback, render_navigation_buttons, render_quick_navigation,
    create_part_navigation_buttons
)

def create_exam_blanc(exam_id=None):
    """
    Crée un examen blanc avec 56 questions Environnement réglementaire et 64 questions Connaissances techniques
    """
    exam_data = load_exam_questions()
    if not exam_data:
        return None
    
    # IMPORTANT: Réinitialiser le seed avant chaque sélection
    if exam_id is not None:
        random.seed(exam_id)
        print(f"DEBUG: Seed {exam_id} appliqué pour sélection des questions")
    
    # Trouver les modules par thème
    env_module = None
    tech_module = None
    
    for module in exam_data['modules']:
        if module.get('theme') == 'Environnement réglementaire':
            env_module = module
        elif module.get('theme') == 'Connaissances techniques':
            tech_module = module
    
    if not env_module or not tech_module:
        return None
    
    # Sélectionner aléatoirement les questions
    env_questions = random.sample(env_module['questions'], min(56, len(env_module['questions'])))
    tech_questions = random.sample(tech_module['questions'], min(64, len(tech_module['questions'])))
    
    # Réassigner les IDs pour être séquentiels avec l'ID d'examen
    for i, q in enumerate(env_questions, 1):
        q['id'] = f"exam{exam_id}_env_{i}" if exam_id else f"env_{i}"
        q['exam_part'] = 1
        q['theme_display'] = 'Environnement réglementaire'
    
    for i, q in enumerate(tech_questions, 1):
        q['id'] = f"exam{exam_id}_tech_{i}" if exam_id else f"tech_{i}"
        q['exam_part'] = 2
        q['theme_display'] = 'Connaissances techniques'
    
    return {
        'part1': {
            'title': 'Partie 1 - Environnement réglementaire',
            'questions': env_questions,
            'target_questions': 56,
            'required_score': 80
        },
        'part2': {
            'title': 'Partie 2 - Connaissances techniques', 
            'questions': tech_questions,
            'target_questions': 64,
            'required_score': 80
        },
        'total_questions': len(env_questions) + len(tech_questions),
        'time_limit_hours': 2,
        'exam_id': exam_id
    }

def show_exam_blanc_interface():
    """Interface principale pour l'examen blanc"""
    if not st.session_state.exam_blanc_questions:
        st.error("❌ Données d'examen blanc non disponibles")
        return
    
    exam_data = st.session_state.exam_blanc_questions
    current_part = st.session_state.exam_blanc_part
    
    # Déterminer les questions de la partie actuelle
    if current_part == 1:
        questions = exam_data['part1']['questions']
        part_title = exam_data['part1']['title']
    else:
        questions = exam_data['part2']['questions']
        part_title = exam_data['part2']['title']
    
    current_idx = st.session_state.current_question_idx
    
    # Vérifier si on doit changer de partie
    if current_idx >= len(questions):
        if current_part == 1:
            # Passer à la partie 2
            st.session_state.exam_blanc_part = 2
            st.session_state.current_question_idx = 0
            st.rerun()
        else:
            # Examen terminé
            st.session_state.quiz_completed = True
            st.rerun()
        return
    
    current_question = questions[current_idx]
    
    # En-tête de l'examen blanc
    render_question_header(f"🎓 {part_title}")
    
    # Navigation entre les parties
    parts_data = [
        {
            'title': '📋 Partie 1 - Environnement réglementaire',
            'questions': exam_data['part1']['questions'],
            'part_number': 1
        },
        {
            'title': '🔧 Partie 2 - Connaissances techniques',
            'questions': exam_data['part2']['questions'],
            'part_number': 2
        }
    ]
    
    new_part = create_part_navigation_buttons(parts_data, current_part)
    if new_part and new_part != current_part:
        st.session_state.exam_blanc_part = new_part
        st.session_state.current_question_idx = 0
        st.rerun()
    
    # Affichage de la question
    render_question_card(current_idx + 1, current_question['question'])
    
    # Options de réponse
    unique_question_id = current_question['id']
    radio_key = f"exam_{current_question['id']}"
    user_choice = render_answer_options(current_question['options'], unique_question_id, radio_key)
    
    # Stocker le choix actuel pour les boutons
    st.session_state.current_user_choice = user_choice
    
    # Feedback immédiat
    render_answer_feedback(unique_question_id)
    
    # Boutons de navigation
    nav_result = render_navigation_buttons(
        current_idx=current_idx,
        total_questions=len(questions),
        unique_question_id=unique_question_id,
        has_next_part=(current_part == 1),
        next_part_label="Partie 2",
        is_last_section=(current_part == 2),
        auto_save_func=auto_save
    )
    
    # Gérer le passage à la partie suivante
    if nav_result == "next_part":
        st.session_state.exam_blanc_part = 2
        st.session_state.current_question_idx = 0
        st.rerun()
    
    # Navigation rapide
    render_quick_navigation(
        questions=questions,
        current_idx=current_idx,
        exam_part=current_part,
        title_suffix=part_title
    )

def calculate_exam_blanc_score():
    """Calcule les scores détaillés pour l'examen blanc"""
    if not st.session_state.exam_blanc_questions:
        return None
    
    exam_data = st.session_state.exam_blanc_questions
    
    # Partie 1 - Environnement réglementaire
    part1_correct = 0
    part1_total = len(exam_data['part1']['questions'])
    
    for question in exam_data['part1']['questions']:
        if question['id'] in st.session_state.user_answers:
            if st.session_state.user_answers[question['id']] == question['correct_answer']:
                part1_correct += 1
    
    # Partie 2 - Connaissances techniques
    part2_correct = 0
    part2_total = len(exam_data['part2']['questions'])
    
    for question in exam_data['part2']['questions']:
        if question['id'] in st.session_state.user_answers:
            if st.session_state.user_answers[question['id']] == question['correct_answer']:
                part2_correct += 1
    
    # Scores calculés
    part1_score = (part1_correct / part1_total * 100) if part1_total > 0 else 0
    part2_score = (part2_correct / part2_total * 100) if part2_total > 0 else 0
    
    # Score global
    total_correct = part1_correct + part2_correct
    total_questions = part1_total + part2_total
    overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'part1': {
            'score': part1_score,
            'correct': part1_correct,
            'total': part1_total
        },
        'part2': {
            'score': part2_score,
            'correct': part2_correct,
            'total': part2_total
        },
        'overall': {
            'score': overall_score,
            'correct': total_correct,
            'total': total_questions
        }
    }

def show_exam_blanc_results():
    """Affiche les résultats de l'examen blanc"""
    if not st.session_state.exam_blanc_questions:
        st.error("❌ Données d'examen blanc non disponibles")
        return
    
    # Calculer les scores
    scores = calculate_exam_blanc_score()
    if not scores:
        st.error("❌ Impossible de calculer les scores")
        return
    
    exam_data = st.session_state.exam_blanc_questions
    exam_id = st.session_state.get('current_exam_blanc_id', '???')
    
    # En-tête des résultats
    st.markdown(f"""
    <div class="main-header">
        <h1>🎓 Résultats Examen Blanc #{exam_id}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Temps écoulé
    if st.session_state.start_time:
        elapsed = datetime.now() - st.session_state.start_time
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        elapsed_hours = elapsed_minutes // 60
        elapsed_mins = elapsed_minutes % 60
        
        # Indicateur de couleur selon le temps
        if elapsed_minutes > 120:  # Plus de 2h
            time_color = '#dc3545'
            time_icon = '🔴'
            time_status = 'Temps dépassé'
        elif elapsed_minutes > 90:  # Plus de 1h30
            time_color = '#ffc107'
            time_icon = '🟡'
            time_status = 'Attention au temps'
        else:
            time_color = '#28a745'
            time_icon = '🟢'
            time_status = 'Bon timing'
        
        st.markdown(f"""
        <div class="metric-card" style="text-align: center; margin-bottom: 2rem;">
            <h3 style="color: {time_color};">{time_icon} Temps écoulé: {elapsed_hours}h{elapsed_mins:02d}m</h3>
            <p style="color: {time_color}; font-weight: bold;">{time_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Résultats par parties
    col1, col2, col3 = st.columns(3)
    
    # Partie 1
    with col1:
        part1_score = scores['part1']['score']
        part1_status = "✅ Réussi" if part1_score >= 80 else "❌ Échec"
        part1_color = "#28a745" if part1_score >= 80 else "#dc3545"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {part1_color};">
            <h3>📋 Partie 1</h3>
            <h2 style="color: {part1_color};">{part1_score:.1f}%</h2>
            <p><strong>{scores['part1']['correct']}/{scores['part1']['total']}</strong> correctes</p>
            <p style="color: {part1_color}; font-weight: bold;">{part1_status}</p>
            <p style="font-size: 0.9em;">Environnement réglementaire</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Partie 2
    with col2:
        part2_score = scores['part2']['score']
        part2_status = "✅ Réussi" if part2_score >= 80 else "❌ Échec"
        part2_color = "#28a745" if part2_score >= 80 else "#dc3545"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {part2_color};">
            <h3>🔧 Partie 2</h3>
            <h2 style="color: {part2_color};">{part2_score:.1f}%</h2>
            <p><strong>{scores['part2']['correct']}/{scores['part2']['total']}</strong> correctes</p>
            <p style="color: {part2_color}; font-weight: bold;">{part2_status}</p>
            <p style="font-size: 0.9em;">Connaissances techniques</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Score global
    with col3:
        overall_score = scores['overall']['score']
        both_passed = part1_score >= 80 and part2_score >= 80
        overall_status = "🎉 ADMIS" if both_passed else "📚 À REPRENDRE"
        overall_color = "#28a745" if both_passed else "#dc3545"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {overall_color};">
            <h3>🎯 Score Global</h3>
            <h2 style="color: {overall_color};">{overall_score:.1f}%</h2>
            <p><strong>{scores['overall']['correct']}/{scores['overall']['total']}</strong> correctes</p>
            <p style="color: {overall_color}; font-weight: bold; font-size: 1.1em;">{overall_status}</p>
            <p style="font-size: 0.9em;">Seuil: 80% par partie</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Message de résultat
    if both_passed:
        st.success("""
        🎉 **Félicitations !** Vous avez réussi l'examen blanc AMF !
        
        ✅ Les deux parties sont validées avec un score ≥ 80%
        """)
    else:
        failed_parts = []
        if part1_score < 80:
            failed_parts.append("Partie 1 (Environnement réglementaire)")
        if part2_score < 80:
            failed_parts.append("Partie 2 (Connaissances techniques)")
        
        st.error(f"""
        📚 **Examen non validé**
        
        ❌ Partie(s) à retravailler : {', '.join(failed_parts)}
        
        💡 **Conseil :** Révisez les modules correspondants et tentez un nouvel examen blanc.
        """)
    
    # Boutons d'actions
    st.subheader("🎯 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Bouton pour réviser les erreurs - VERSION CORRIGÉE
        incorrect_questions = []
        
        # Collecter toutes les questions incorrectes
        for question in exam_data['part1']['questions']:
            question_id = question['id']
            if question_id in st.session_state.user_answers:
                user_answer = st.session_state.user_answers[question_id]
                correct_answer = question['correct_answer']
                if user_answer != correct_answer:
                    incorrect_questions.append(question)
        
        for question in exam_data['part2']['questions']:
            question_id = question['id']
            if question_id in st.session_state.user_answers:
                user_answer = st.session_state.user_answers[question_id]
                correct_answer = question['correct_answer']
                if user_answer != correct_answer:
                    incorrect_questions.append(question)
        
        # Toujours afficher le bouton, même s'il n'y a pas d'erreurs
        if len(incorrect_questions) > 0:
            if st.button("❌ Réviser les erreurs", type="secondary", use_container_width=True, key="review_errors_btn"):
                # Créer une session de révision des erreurs pour l'examen blanc
                st.session_state.exam_blanc_review_questions = incorrect_questions
                st.session_state.current_question_idx = 0
                st.session_state.quiz_started = True
                st.session_state.quiz_completed = False
                st.session_state.quiz_mode = 'exam_blanc_review'
                st.session_state.start_time = datetime.now()
                st.rerun()
            
            st.caption(f"📝 {len(incorrect_questions)} erreur(s) à revoir")
        else:
            # Bouton désactivé mais visible si pas d'erreurs
            st.button("❌ Réviser les erreurs", 
                     type="secondary", 
                     use_container_width=True,
                     disabled=True,
                     key="review_errors_disabled_btn",
                     help="Aucune erreur à réviser - Parfait score !")
            st.success("🎉 Aucune erreur à réviser !")
    
    with col2:
        # Bouton pour refaire l'examen
        if st.button("🔄 Refaire l'examen", type="secondary", use_container_width=True):
            # Supprimer toutes les réponses de cet examen
            keys_to_remove = []
            for key in st.session_state.user_answers.keys():
                if key.startswith(f'exam{exam_id}_'):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del st.session_state.user_answers[key]
            
            # Redémarrer l'examen
            st.session_state.current_question_idx = 0
            st.session_state.exam_blanc_part = 1
            st.session_state.quiz_started = True
            st.session_state.quiz_completed = False
            st.session_state.start_time = datetime.now()
            st.session_state.quiz_mode = 'exam_blanc'
            
            # Sauvegarder les changements
            from modules.persistence import save_user_progress
            save_user_progress(force_save=True)
            st.rerun()
    
    with col3:
        # Bouton retour au menu
        if st.button("🏠 Retour au menu", type="secondary", use_container_width=True):
            from modules.persistence import save_user_progress
            save_user_progress()
            st.session_state.quiz_started = False
            st.session_state.quiz_completed = False
            st.session_state.exam_blanc_questions = None
            st.session_state.current_exam_blanc_id = None
            if 'exam_blanc_review_questions' in st.session_state:
                del st.session_state.exam_blanc_review_questions
            st.rerun()
    
    # Graphique de performance
    st.subheader("📊 Analyse détaillée")
    
    # Données pour le graphique
    categories = ['Partie 1\n(Env. réglementaire)', 'Partie 2\n(Conn. techniques)', 'Score Global']
    scores_list = [part1_score, part2_score, overall_score]
    colors = [part1_color, part2_color, overall_color]
    
    # Créer le graphique
    fig = go.Figure()
    
    # Barres de score
    fig.add_trace(go.Bar(
        x=categories,
        y=scores_list,
        marker_color=colors,
        text=[f"{score:.1f}%" for score in scores_list],
        textposition='inside',
        textfont=dict(color='white', size=14, family="Arial"),
        showlegend=False
    ))
    
    # Ligne de seuil à 80%
    fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                  annotation_text="Seuil de réussite (80%)")
    
    fig.update_layout(
        title="Performance par partie",
        yaxis=dict(title="Score (%)", range=[0, 100]),
        xaxis=dict(title=""),
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations
    st.subheader("💡 Recommandations")
    
    if both_passed:
        st.info("""
        🎯 **Excellent travail !** Votre préparation semble solide.
        
        **Suggestions pour maintenir votre niveau :**
        - Continuez à pratiquer régulièrement
        - Révisez les questions que vous avez ratées
        - Tentez d'autres examens blancs pour confirmer vos acquis
        """)
    else:
        if part1_score < 80:
            st.warning("""
            📋 **Partie 1 à retravailler** (Environnement réglementaire)
            
            **Modules recommandés :**
            - M1 : Cadre institutionnel
            - M2 : Cadre réglementaire
            - M3 : Déontologie
            """)
        
        if part2_score < 80:
            st.warning("""
            🔧 **Partie 2 à retravailler** (Connaissances techniques)
            
            **Modules recommandés :**
            - M4 : Instruments financiers
            - M5 : Gestion de portefeuille  
            - M6 : Analyse financière
            - Et les autres modules techniques selon vos lacunes
            """)
    
    # Statistiques supplémentaires
    with st.expander("📈 Statistiques détaillées"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Répartition des réponses :**")
            total_questions = scores['overall']['total']
            correct_answers = scores['overall']['correct']
            incorrect_answers = total_questions - correct_answers
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Correctes', 'Incorrectes'],
                values=[correct_answers, incorrect_answers],
                marker_colors=['#28a745', '#dc3545'],
                textinfo='label+percent',
                textfont_size=12
            )])
            
            fig_pie.update_layout(
                title="Répartition globale",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("**Détails par partie :**")
            st.write(f"**Partie 1 :** {scores['part1']['correct']}/{scores['part1']['total']} ({part1_score:.1f}%)")
            st.write(f"**Partie 2 :** {scores['part2']['correct']}/{scores['part2']['total']} ({part2_score:.1f}%)")
            st.write(f"**Total :** {scores['overall']['correct']}/{scores['overall']['total']} ({overall_score:.1f}%)")
            
            if st.session_state.start_time:
                st.write(f"**Durée :** {elapsed_hours}h{elapsed_mins:02d}m")
                avg_time_per_q = elapsed_minutes / total_questions
                st.write(f"**Temps moyen/question :** {avg_time_per_q:.1f} min")

def show_exam_blanc_review_interface():
    """Interface pour réviser les erreurs d'un examen blanc"""
    if 'exam_blanc_review_questions' not in st.session_state or not st.session_state.exam_blanc_review_questions:
        st.error("❌ Aucune question de révision disponible")
        return
    
    questions = st.session_state.exam_blanc_review_questions
    current_idx = st.session_state.current_question_idx
    exam_id = st.session_state.get('current_exam_blanc_id', '???')
    
    if current_idx >= len(questions):
        st.session_state.quiz_completed = True
        st.rerun()
        return
    
    current_question = questions[current_idx]
    
    # En-tête de révision
    render_question_header(f"🔄 Révision Erreurs - Examen #{exam_id}")
    
    # Info sur la révision
    st.info(f"📝 Question {current_idx + 1} sur {len(questions)} erreur(s) à revoir")
    
    # Barre de progression
    progress = (current_idx + 1) / len(questions)
    st.progress(progress)
    
    # Affichage de la question
    render_question_card(current_idx + 1, current_question['question'])
    
    # Afficher la partie/thème de la question
    part_info = "📋 Partie 1" if current_question.get('exam_part') == 1 else "🔧 Partie 2"
    theme_info = current_question.get('theme_display', 'Non spécifié')
    st.caption(f"{part_info} - {theme_info}")
    
    # Options de réponse
    unique_question_id = current_question['id']
    radio_key = f"review_{current_question['id']}"
    user_choice = render_answer_options(current_question['options'], unique_question_id, radio_key)
    
    # Stocker le choix actuel pour les boutons
    st.session_state.current_user_choice = user_choice
    
    # Afficher systématiquement la réponse correcte et l'erreur commise
    if unique_question_id in st.session_state.user_answers:
        user_answer = st.session_state.user_answers[unique_question_id]
        correct_answer = current_question['correct_answer']
        options = current_question['options']
        
        # Afficher l'erreur commise
        st.error(f"❌ **Votre erreur :** {user_answer} - {options[user_answer]}")
        
        # Afficher la bonne réponse
        st.success(f"✅ **Bonne réponse :** {correct_answer} - {options[correct_answer]}")
        
        # Explication si disponible
        if 'explanation' in current_question and current_question['explanation']:
            st.info(f"💡 **Explication :** {current_question['explanation']}")
    
    # Boutons de navigation pour la révision
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Précédent", use_container_width=True):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col2:
        # Bouton "Compris" pour passer à la suivante
        if st.button("✅ Compris", type="primary", use_container_width=True):
            if current_idx < len(questions) - 1:
                st.session_state.current_question_idx += 1
                st.rerun()
            else:
                # Fin de la révision
                st.success("🎉 Révision terminée !")
                st.balloons()
                st.session_state.quiz_completed = True
                st.rerun()
    
    with col3:
        if current_idx < len(questions) - 1:
            if st.button("➡️ Suivant", use_container_width=True):
                st.session_state.current_question_idx += 1
                st.rerun()
        else:
            if st.button("🏁 Terminer", type="primary", use_container_width=True):
                st.session_state.quiz_completed = True
                st.rerun()
    
    # Navigation rapide pour la révision
    if len(questions) > 1:
        st.markdown("**🔍 Navigation rapide**")
        
        cols_per_row = 10
        for i in range(0, len(questions), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, q_idx in enumerate(range(i, min(i + cols_per_row, len(questions)))):
                with cols[j]:
                    button_type = "primary" if q_idx == current_idx else "secondary"
                    if st.button(f"{q_idx + 1}", key=f"nav_review_{q_idx}", 
                               type=button_type, use_container_width=True):
                        st.session_state.current_question_idx = q_idx
                        st.rerun()