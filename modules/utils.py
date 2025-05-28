import streamlit as st

def get_user_progress(data):
    """Calcule la progression globale de l'utilisateur"""
    total_questions = data['metadata']['total_questions']
    # Compter seulement les questions avec des identifiants uniques réellement répondues
    answered_questions = 0
    for module in data['modules']:
        for question in module['questions']:
            unique_q_id = f"{module['id']}_{question['id']}"
            if unique_q_id in st.session_state.user_answers:
                answered_questions += 1
    return answered_questions, total_questions

def calculate_score(module_questions, user_answers, module_id):
    """Calcule le score pour un module donné"""
    if not user_answers:
        return 0, 0
    
    correct = 0
    total = 0
    
    for question in module_questions:
        # Utiliser un identifiant unique combinant module_id et question_id
        unique_q_id = f"{module_id}_{question['id']}"
        if unique_q_id in user_answers:
            total += 1
            if user_answers[unique_q_id] == question['correct_answer']:
                correct += 1
    
    return correct, total

def get_performance_level(score):
    """Détermine le niveau de performance basé sur le score"""
    if score >= 90:
        return "🎖️ Excellent", "success"
    elif score >= 80:
        return "🏆 Très bien", "success"
    elif score >= 70:
        return "👍 Bien", "info"
    elif score >= 60:
        return "📚 Correct", "warning"
    else:
        return "🔄 À améliorer", "error"