import json
import os
import streamlit as st
from datetime import datetime
from pathlib import Path

# Configuration des fichiers de sauvegarde - MODIFIÉ vers checkpoint
SAVE_DIRECTORY = "checkpoint"
PROGRESS_FILE = f"{SAVE_DIRECTORY}/user_progress.json"
BACKUP_FILE = f"{SAVE_DIRECTORY}/user_progress_backup.json"

def ensure_save_directory():
    """Crée le répertoire de sauvegarde s'il n'existe pas"""
    try:
        Path(SAVE_DIRECTORY).mkdir(parents=True, exist_ok=True)
        print(f"✅ Dossier checkpoint créé/vérifié: {os.path.abspath(SAVE_DIRECTORY)}")
    except Exception as e:
        print(f"❌ Erreur création dossier: {e}")

def test_directory_creation():
    """Fonction de test pour vérifier la création du dossier"""
    print(f"🔍 Test création dossier: {SAVE_DIRECTORY}")
    ensure_save_directory()
    
    # Créer un fichier de test
    test_file = f"{SAVE_DIRECTORY}/test.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test de création de fichier")
        print(f"✅ Fichier test créé: {test_file}")
        
        # Supprimer le fichier de test
        os.remove(test_file)
        print("✅ Fichier test supprimé")
        return True
    except Exception as e:
        print(f"❌ Erreur création fichier test: {e}")
        return False

def get_default_progress():
    """Retourne la structure par défaut de progression"""
    return {
        "user_answers": {},
        "last_updated": datetime.now().isoformat(),
        "version": "1.0",
        "statistics": {
            "total_questions_answered": 0,
            "total_sessions": 0,
            "last_session": None,
            "modules_completed": [],
            "exam_blanc_attempts": []
        }
    }

def load_user_progress():
    """
    Charge la progression de l'utilisateur depuis le fichier JSON
    
    Returns:
        dict: Données de progression ou données par défaut si erreur
    """
    ensure_save_directory()
    
    try:
        # Essayer de charger le fichier principal
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Valider la structure des données
            if validate_progress_data(data):
                print(f"✅ Progression chargée: {len(data.get('user_answers', {}))} réponses")
                return data
            else:
                print("⚠️ Structure de données invalide, tentative de récupération du backup")
                
        # Essayer le fichier de backup
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if validate_progress_data(data):
                print("✅ Progression récupérée depuis le backup")
                return data
        
        print("📝 Nouvelle session: progression initialisée")
        return get_default_progress()
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return get_default_progress()

def validate_progress_data(data):
    """
    Valide la structure des données de progression
    
    Args:
        data: Données à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not isinstance(data, dict):
        return False
        
    required_keys = ["user_answers", "last_updated", "version"]
    return all(key in data for key in required_keys)

def save_user_progress(force_save=False):
    """
    Sauvegarde la progression de l'utilisateur
    
    Args:
        force_save: Force la sauvegarde même si peu de changements
    """
    try:
        ensure_save_directory()
        
        # Préparer les données à sauvegarder
        progress_data = {
            "user_answers": st.session_state.user_answers,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
            "statistics": calculate_user_statistics()
        }
        
        # Créer un backup du fichier existant
        if os.path.exists(PROGRESS_FILE):
            try:
                os.replace(PROGRESS_FILE, BACKUP_FILE)
            except Exception as e:
                print(f"⚠️ Impossible de créer le backup: {e}")
        
        # Sauvegarder les nouvelles données
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        # Mettre à jour les métadonnées de session
        if 'last_save_time' not in st.session_state:
            st.session_state.last_save_time = datetime.now()
        else:
            st.session_state.last_save_time = datetime.now()
            
        print(f"💾 Progression sauvegardée: {len(st.session_state.user_answers)} réponses")
        return True
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def calculate_user_statistics():
    """
    Calcule les statistiques de l'utilisateur
    
    Returns:
        dict: Statistiques calculées
    """
    user_answers = st.session_state.get('user_answers', {})
    
    # Compter les modules avec des réponses
    modules_with_answers = set()
    for answer_key in user_answers.keys():
        if '_' in answer_key:
            module_id = answer_key.split('_')[0]
            modules_with_answers.add(module_id)
    
    # Compter les tentatives d'examen blanc
    exam_blanc_questions = [key for key in user_answers.keys() 
                          if key.startswith('env_') or key.startswith('tech_')]
    
    return {
        "total_questions_answered": len(user_answers),
        "total_sessions": st.session_state.get('session_count', 1),
        "last_session": datetime.now().isoformat(),
        "modules_with_progress": list(modules_with_answers),
        "exam_blanc_questions_answered": len(exam_blanc_questions)
    }

def auto_save_progress():
    """
    Sauvegarde automatique intelligente
    Sauvegarde seulement si des changements significatifs ont eu lieu
    """
    if 'user_answers' not in st.session_state:
        return
    
    # Vérifier s'il y a eu des changements depuis la dernière sauvegarde
    current_answers_count = len(st.session_state.user_answers)
    last_saved_count = st.session_state.get('last_saved_answers_count', 0)
    
    # Sauvegarder si :
    # 1. Il y a plus de 5 nouvelles réponses
    # 2. Plus de 5 minutes se sont écoulées depuis la dernière sauvegarde
    # 3. Force save demandée
    should_save = (
        current_answers_count - last_saved_count >= 5 or
        (st.session_state.get('last_save_time') and 
         (datetime.now() - st.session_state.last_save_time).seconds > 300)
    )
    
    if should_save:
        if save_user_progress():
            st.session_state.last_saved_answers_count = current_answers_count

def reset_user_progress():
    """
    Réinitialise complètement la progression de l'utilisateur
    """
    try:
        # Créer un backup avant la réinitialisation
        if os.path.exists(PROGRESS_FILE):
            backup_reset_file = f"{SAVE_DIRECTORY}/progress_before_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.replace(PROGRESS_FILE, backup_reset_file)
            print(f"💾 Backup créé avant réinitialisation: {backup_reset_file}")
        
        # Réinitialiser en mémoire
        st.session_state.user_answers = {}
        st.session_state.last_saved_answers_count = 0
        
        # Sauvegarder l'état vide
        save_user_progress(force_save=True)
        
        print("🔄 Progression réinitialisée avec succès")
        return True
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la réinitialisation: {e}")
        return False

def initialize_session_with_persistence():
    """
    Initialise la session avec la progression sauvegardée
    À appeler au début de l'application
    """
    # S'assurer que le dossier existe dès le démarrage
    ensure_save_directory()
    
    # Charger la progression sauvegardée
    saved_progress = load_user_progress()
    
    # Restaurer les réponses utilisateur
    st.session_state.user_answers = saved_progress.get('user_answers', {})
    
    # Initialiser les autres variables de session si nécessaire
    defaults = {
        'current_module': None,
        'current_question_idx': 0,
        'quiz_mode': 'practice',
        'quiz_started': False,
        'quiz_completed': False,
        'start_time': None,
        'theme_preference': 'auto',
        'show_explanations': True,
        'randomize_questions': False,
        'exam_blanc_data': None,
        'exam_blanc_part': 1,
        'exam_blanc_questions': None,
        'session_count': saved_progress.get('statistics', {}).get('total_sessions', 0) + 1,
        'last_saved_answers_count': len(st.session_state.user_answers)
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Afficher des informations de restauration si des données ont été chargées
    if st.session_state.user_answers:
        answers_count = len(st.session_state.user_answers)
        last_updated = saved_progress.get('last_updated', 'Inconnu')
        
        # Afficher dans la sidebar avec un message discret
        with st.sidebar:
            with st.expander("📊 Progression restaurée", expanded=False):
                st.info(f"✅ {answers_count} réponses restaurées")
                st.caption(f"Dernière mise à jour: {last_updated[:16].replace('T', ' ')}")

def show_progress_info():
    """
    Affiche des informations sur la progression dans la sidebar
    """
    if st.session_state.get('user_answers'):
        answers_count = len(st.session_state.user_answers)
        
        # Calculer le pourcentage de progression global approximatif
        estimated_total = 560  # Basé sur vos métadonnées
        progress_percentage = min((answers_count / estimated_total) * 100, 100)
        
        st.sidebar.markdown(f"""
        <div class="stats-card">
            <h4>💾 Sauvegarde Auto</h4>
            <p><strong>{answers_count}</strong> réponses sauvées</p>
            <p><strong>{progress_percentage:.1f}%</strong> de progression</p>
            <p style="font-size: 0.8em; opacity: 0.8;">Sauvegarde automatique active</p>
        </div>
        """, unsafe_allow_html=True)

# Fonction hook pour sauvegarder à chaque réponse validée
def on_answer_validated():
    """
    À appeler chaque fois qu'une réponse est validée
    """
    auto_save_progress()