import streamlit as st
from datetime import datetime
from modules.config import auto_save

def render_question_header(title, subtitle=None):
    """Affiche l'en-tête d'une question"""
    header_html = f"""
    <div class="quiz-header" style="padding: 0.8rem; margin-bottom: 1rem;">
        <h2 style="margin: 0; color: var(--primary-color); font-size: 1.4rem;">{title}</h2>
    """
    if subtitle:
        header_html += f'<p style="margin: 0.3rem 0 0 0; font-size: 1rem; opacity: 0.8;">{subtitle}</p>'
    
    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

def render_question_card(question_number, question_text):
    """Affiche la carte de question"""
    st.markdown(f"""
    <div class="question-card" style="padding: 1rem; margin: 1rem 0;">
        <h3 style="margin: 0 0 0.8rem 0; font-size: 1.2rem;">Question {question_number}</h3>
        <p style="margin: 0; font-size: 1.05rem; line-height: 1.4;">{question_text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_answer_options(options, unique_question_id, radio_key):
    """Affiche les options de réponse avec pré-sélection si existante"""
    st.markdown("**Choisissez votre réponse :**")
    
    # Récupérer la réponse précédente si elle existe
    previous_answer = st.session_state.user_answers.get(unique_question_id, None)
    
    # Déterminer l'index de la réponse précédente
    previous_index = None
    if previous_answer:
        option_keys = list(options.keys())
        if previous_answer in option_keys:
            previous_index = option_keys.index(previous_answer)
    
    user_choice = st.radio(
        "Options",
        list(options.keys()),
        format_func=lambda x: f"{x} - {options[x]}",
        key=radio_key,
        index=previous_index,
        label_visibility="collapsed"
    )
    
    return user_choice

def render_answer_feedback(unique_question_id, show_saved_message=True):
    """
    Affiche le feedback si la question a été répondue
    
    Args:
        unique_question_id: ID unique de la question
        show_saved_message: Si True, affiche "Réponse enregistrée" (pour examen blanc)
                           Si False, n'affiche pas ce message (pour entraînement)
    """
    if unique_question_id in st.session_state.user_answers and show_saved_message:
        st.success("✅ Réponse enregistrée")

def render_navigation_buttons(current_idx, total_questions, unique_question_id, 
                            has_next_part=False, next_part_label="", 
                            is_last_section=False, auto_save_func=None):
    """
    Affiche les boutons de navigation avec gestion des couleurs
    
    Args:
        current_idx: Index de la question actuelle
        total_questions: Nombre total de questions dans la section
        unique_question_id: ID unique de la question
        has_next_part: Si il y a une partie suivante
        next_part_label: Label de la partie suivante
        is_last_section: Si c'est la dernière section
        auto_save_func: Fonction de sauvegarde automatique
    """
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # Vérifier si la question actuelle a déjà une réponse validée
    is_answered = unique_question_id in st.session_state.user_answers
    
    # Récupérer le choix actuel
    user_choice = st.session_state.get('current_user_choice', None)
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Précédent", use_container_width=True):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col2:
        # Bouton Valider - couleur selon l'état
        if user_choice:
            # Si la réponse est déjà validée, bouton normal
            button_type = "secondary" if is_answered else "primary"
            if st.button("💾 Valider", type=button_type, use_container_width=True):
                st.session_state.user_answers[unique_question_id] = user_choice
                
                # Sauvegarder automatiquement
                if auto_save_func:
                    try:
                        auto_save_func()
                        print(f"✅ Réponse validée et sauvegardée: {unique_question_id} = {user_choice}")
                    except Exception as e:
                        print(f"⚠️ Erreur lors de la sauvegarde automatique: {e}")
                
                st.rerun()
        else:
            # Bouton désactivé visuellement quand aucune réponse n'est sélectionnée
            st.button("💾 Valider", type="primary", use_container_width=True, disabled=True)
            if not user_choice:
                st.caption("⚠️ Sélectionnez une réponse pour valider")
    
    with col3:
        if current_idx < total_questions - 1:
            # Bouton Suivant - rouge si la question actuelle est répondue
            button_type = "primary" if is_answered else "secondary"
            if st.button("➡️ Suivant", type=button_type, use_container_width=True):
                if unique_question_id in st.session_state.user_answers:
                    st.session_state.current_question_idx += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Veuillez d'abord valider votre réponse")
        elif has_next_part and not is_last_section:
            # Bouton Partie suivante - rouge si la question actuelle est répondue
            button_type = "primary" if is_answered else "secondary"
            if st.button(f"🔄 {next_part_label}", type=button_type, use_container_width=True):
                if unique_question_id in st.session_state.user_answers:
                    # Cette logique sera gérée par le fichier appelant
                    return "next_part"
                else:
                    st.warning("⚠️ Veuillez d'abord valider votre réponse")
        else:
            # Bouton Terminer - rouge si la question actuelle est répondue
            button_type = "primary" if is_answered else "secondary"
            if st.button("🏁 Terminer", type=button_type, use_container_width=True):
                if unique_question_id in st.session_state.user_answers:
                    st.session_state.quiz_completed = True
                    st.rerun()
                else:
                    st.warning("⚠️ Veuillez d'abord valider votre réponse")
    
    return None

# Modifier render_quick_navigation pour marquer la navigation manuelle
def render_quick_navigation(questions, current_idx, module_id=None, exam_part=None, title_suffix=""):
    """
    Affiche la navigation rapide par numéro de question
    """
    if len(questions) <= 1:
        return
    
    title = f"**🔍 Navigation rapide** ({len(questions)} questions)"
    if title_suffix:
        title += f" - {title_suffix}"
    
    st.markdown(title)
    
    # Créer une grille compacte de boutons pour la navigation
    cols_per_row = 15
    question_numbers = list(range(1, len(questions) + 1))
    
    for i in range(0, len(question_numbers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, q_num in enumerate(question_numbers[i:i+cols_per_row]):
            with cols[j]:
                q_idx = q_num - 1
                question = questions[q_idx]
                
                # Générer l'ID unique selon le contexte
                if module_id:
                    unique_question_id = f"{module_id}_{question['id']}"
                    nav_key = f"nav_{q_num}_{module_id}"
                else:
                    unique_question_id = question['id']
                    nav_key = f"nav_exam_{exam_part}_{q_num}"
                
                # Déterminer le style du bouton selon le statut
                if q_idx == current_idx:
                    button_type = "primary"
                    icon = "👁️"
                elif unique_question_id in st.session_state.user_answers:
                    icon = "✅"
                    button_type = "secondary"
                else:
                    icon = "🔵"
                    button_type = "secondary"
                
                if st.button(f"{icon}{q_num}", key=nav_key, 
                           type=button_type, use_container_width=True):
                    # Marquer que l'utilisateur a utilisé la navigation manuelle
                    st.session_state.manual_navigation_used = True
                    st.session_state.current_question_idx = q_idx
                    st.rerun()

def get_quiz_progress_info(questions, module_id=None):
    """
    Calcule les informations de progression d'un quiz
    
    Returns:
        dict: Informations de progression (answered, total, progress_pct)
    """
    if module_id:
        # Quiz standard
        answered = sum(1 for q in questions if f"{module_id}_{q['id']}" in st.session_state.user_answers)
    else:
        # Examen blanc
        answered = sum(1 for q in questions if q['id'] in st.session_state.user_answers)
    
    total = len(questions)
    progress_pct = (answered / total * 100) if total > 0 else 0
    
    return {
        'answered': answered,
        'total': total,
        'progress_pct': progress_pct
    }

def handle_auto_positioning(questions, module_id=None):
    """
    Positionne automatiquement sur la dernière question répondue + 1
    Détecte automatiquement si c'est un nouveau démarrage de quiz
    
    Args:
        questions: Liste des questions
        module_id: ID du module (None pour examen blanc)
    """
    # Détection intelligente : nouveau démarrage si on est à l'index 0 
    # ET qu'aucun quiz n'était en cours (quiz_started vient de passer à True)
    current_idx = st.session_state.current_question_idx
    
    # Si on n'est pas à l'index 0, l'utilisateur a déjà navigué
    if current_idx != 0:
        return
    
    # Créer une clé de session pour ce module/mode spécifique
    session_key = f"session_{module_id}_{st.session_state.get('quiz_mode', 'practice')}"
    current_session = st.session_state.get('session_id', id(st.session_state))
    
    # Si c'est la même session pour ce module, ne pas repositionner
    if st.session_state.get(session_key) == current_session:
        return
    
    # Marquer cette session pour ce module
    st.session_state[session_key] = current_session
    
    # Chercher la dernière question répondue
    last_answered_idx = -1
    for i, question in enumerate(questions):
        if module_id:
            unique_question_id = f"{module_id}_{question['id']}"
        else:
            unique_question_id = question['id']
        
        if unique_question_id in st.session_state.user_answers:
            last_answered_idx = i
    
    # Se positionner sur la question suivante seulement s'il y a des réponses
    if last_answered_idx >= 0:
        next_position = min(last_answered_idx + 1, len(questions) - 1)
        st.session_state.current_question_idx = next_position

def create_part_navigation_buttons(parts_data, current_part):
    """
    Crée les boutons de navigation entre les parties
    
    Args:
        parts_data: Liste des données de parties [{'title': str, 'questions': list, 'part_number': int}]
        current_part: Numéro de la partie actuelle
    
    Returns:
        int or None: Nouvelle partie sélectionnée ou None
    """
    if len(parts_data) <= 1:
        return None
    
    st.subheader("📚 Navigation entre les parties")
    cols = st.columns(len(parts_data))
    
    for i, part_data in enumerate(parts_data):
        with cols[i]:
            part_num = part_data['part_number']
            part_title = part_data['title']
            questions = part_data['questions']
            
            # Calculer les questions répondues pour cette partie
            answered = sum(1 for q in questions if q['id'] in st.session_state.user_answers)
            total = len(questions)
            progress_text = f"{answered}/{total}"
            
            button_type = "primary" if current_part == part_num else "secondary"
            button_label = f"{part_title} ({progress_text})"
            
            if st.button(button_label, type=button_type, use_container_width=True):
                if current_part != part_num:
                    return part_num
    
    return None