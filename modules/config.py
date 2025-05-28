import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

def get_theme_colors():
    """Détecte le thème actuel et retourne les couleurs appropriées"""
    return {
        'light': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#212529',
            'text_secondary': '#6c757d',
            'border': '#e9ecef',
            'shadow': 'rgba(0,0,0,0.1)'
        },
        'dark': {
            'primary': '#8b9cf7',
            'secondary': '#9d7bc8',
            'success': '#20c997',
            'danger': '#fd7e79',
            'warning': '#ffda6a',
            'info': '#39c0ed',
            'light': '#495057',
            'dark': '#212529',
            'background': '#0e1117',
            'surface': '#262730',
            'text': '#fafafa',
            'text_secondary': '#a3a8b8',
            'border': '#30363d',
            'shadow': 'rgba(0,0,0,0.3)'
        }
    }

def inject_custom_css():
    """Injecte le CSS personnalisé adaptatif"""
    colors = get_theme_colors()
    
    st.markdown(f"""
    <style>
        /* Variables CSS pour les thèmes */
        :root {{
            --primary-color: {colors['light']['primary']};
            --secondary-color: {colors['light']['secondary']};
            --success-color: {colors['light']['success']};
            --danger-color: {colors['light']['danger']};
            --warning-color: {colors['light']['warning']};
            --info-color: {colors['light']['info']};
            --background-color: {colors['light']['background']};
            --surface-color: {colors['light']['surface']};
            --text-color: {colors['light']['text']};
            --text-secondary: {colors['light']['text_secondary']};
            --border-color: {colors['light']['border']};
            --shadow-color: {colors['light']['shadow']};
        }}
        
        /* Thème sombre */
        @media (prefers-color-scheme: dark) {{
            :root {{
                --primary-color: {colors['dark']['primary']};
                --secondary-color: {colors['dark']['secondary']};
                --success-color: {colors['dark']['success']};
                --danger-color: {colors['dark']['danger']};
                --warning-color: {colors['dark']['warning']};
                --info-color: {colors['dark']['info']};
                --background-color: {colors['dark']['background']};
                --surface-color: {colors['dark']['surface']};
                --text-color: {colors['dark']['text']};
                --text-secondary: {colors['dark']['text_secondary']};
                --border-color: {colors['dark']['border']};
                --shadow-color: {colors['dark']['shadow']};
            }}
        }}
        
        /* Override pour Streamlit dark theme */
        [data-theme="dark"] {{
            --primary-color: {colors['dark']['primary']};
            --secondary-color: {colors['dark']['secondary']};
            --success-color: {colors['dark']['success']};
            --danger-color: {colors['dark']['danger']};
            --warning-color: {colors['dark']['warning']};
            --info-color: {colors['dark']['info']};
            --background-color: {colors['dark']['background']};
            --surface-color: {colors['dark']['surface']};
            --text-color: {colors['dark']['text']};
            --text-secondary: {colors['dark']['text_secondary']};
            --border-color: {colors['dark']['border']};
            --shadow-color: {colors['dark']['shadow']};
        }}
        
        /* Styles principaux */
        .main-header {{
            text-align: center;
            padding: 2rem 1rem;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px var(--shadow-color);
            transition: all 0.3s ease;
        }}
        
        .main-header:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 25px var(--shadow-color);
        }}
        
        .main-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        
        .main-header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .module-card {{
            background: var(--surface-color);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid var(--primary-color);
            margin: 1rem 0;
            box-shadow: 0 2px 10px var(--shadow-color);
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
        }}
        
        .module-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px var(--shadow-color);
        }}
        
        .question-card {{
            background: var(--surface-color);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px var(--shadow-color);
            border: 1px solid var(--border-color);
            margin: 1.5rem 0;
            transition: all 0.3s ease;
        }}
        
        .question-card:hover {{
            box-shadow: 0 6px 25px var(--shadow-color);
        }}
        
        .question-card h3 {{
            color: var(--primary-color);
            margin-bottom: 1rem;
            font-weight: 600;
        }}
        
        .question-card p {{
            color: var(--text-color);
            line-height: 1.6;
            font-size: 1.1rem;
        }}
        
        .stats-card {{
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px var(--shadow-color);
            transition: all 0.3s ease;
            margin-bottom: 1.5rem;
        }}
        
        .stats-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--shadow-color);
        }}
        
        .stats-card h3 {{
            margin: 0 0 1rem 0;
            font-size: 1.2rem;
            font-weight: 600;
        }}
        
        .stats-card h4 {{
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .stats-card p {{
            margin: 0.25rem 0;
            font-size: 1rem;
            opacity: 0.95;
        }}
        
        .metric-card {{
            background: var(--surface-color);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 10px var(--shadow-color);
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px var(--shadow-color);
        }}
        
        .correct-answer {{
            background: rgba(40, 167, 69, 0.1);
            border: 1px solid var(--success-color);
            border-radius: 8px;
            padding: 1rem;
            color: var(--success-color);
            margin: 1rem 0;
            animation: slideIn 0.3s ease;
        }}
        
        .incorrect-answer {{
            background: rgba(220, 53, 69, 0.1);
            border: 1px solid var(--danger-color);
            border-radius: 8px;
            padding: 1rem;
            color: var(--danger-color);
            margin: 1rem 0;
            animation: slideIn 0.3s ease;
        }}
        
        .warning-message {{
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid var(--warning-color);
            border-radius: 8px;
            padding: 1rem;
            color: var(--warning-color);
            margin: 1rem 0;
        }}
        
        .progress-container {{
            background: var(--surface-color);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
        }}
        
        .quiz-header {{
            background: var(--surface-color);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 10px var(--shadow-color);
        }}
        
        .navigation-buttons {{
            padding: 1rem 0;
            border-top: 1px solid var(--border-color);
            margin-top: 2rem;
        }}
        
        .results-header {{
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--success-color) 0%, var(--primary-color) 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px var(--shadow-color);
        }}
        
        .error-review {{
            background: var(--surface-color);
            border-left: 4px solid var(--danger-color);
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid var(--border-color);
        }}
        
        /* Animations */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        .pulse-animation {{
            animation: pulse 2s infinite;
        }}
        
        /* Responsivité améliorée */
        @media (max-width: 768px) {{
            .main-header h1 {{
                font-size: 2rem;
            }}
            
            .question-card {{
                padding: 1.5rem;
            }}
            
            .stats-card {{
                padding: 1rem;
            }}
        }}
        
        /* Amélioration des composants Streamlit */
        .stSelectbox > div > div {{
            background-color: var(--surface-color);
            border-color: var(--border-color);
        }}
        
        .stRadio > div {{
            background-color: var(--surface-color);
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid var(--border-color);
        }}
        
        .stRadio > div > label {{
            margin-bottom: 0.5rem !important;
            padding: 0.5rem 0 !important;
        }}
        
        .stRadio > div > label:not(:last-child) {{
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 0.75rem !important;
            padding-bottom: 0.75rem !important;
        }}
        
        .stButton > button {{
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 10px var(--shadow-color);
        }}
        
        .stExpander {{
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background-color: var(--surface-color);
        }}
        
        .stAlert {{
            border-radius: 8px;
            animation: slideIn 0.3s ease;
        }}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialise toutes les variables de session state"""
    defaults = {
        'current_module': None,
        'current_question_idx': 0,
        'user_answers': {},
        'quiz_mode': 'practice',
        'quiz_started': False,
        'quiz_completed': False,
        'start_time': None,
        'theme_preference': 'auto',
        'show_explanations': True,
        'randomize_questions': False,
        'exam_blanc_data': None,
        'exam_blanc_part': 1,
        'exam_blanc_questions': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Fonctions de sauvegarde simple et efficace
def load_progress():
    """Charge la progression sauvegardée"""
    try:
        if os.path.exists("user_progress.json"):
            with open("user_progress.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ Progression chargée: {len(data.get('user_answers', {}))} réponses")
                return data.get("user_answers", {})
        else:
            print("📝 Aucun fichier de sauvegarde trouvé")
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
    return {}

def save_progress():
    """Sauvegarde la progression actuelle"""
    try:
        data = {
            "user_answers": st.session_state.get("user_answers", {}),
            "last_saved": str(datetime.now())
        }
        with open("user_progress.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Sauvegarde réussie: {len(data['user_answers'])} réponses")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def auto_save():
    """Sauvegarde automatique à chaque réponse"""
    if 'user_answers' in st.session_state:
        current_count = len(st.session_state.user_answers)
        last_count = st.session_state.get('last_save_count', 0)
        
        print(f"🔍 Auto-save: {current_count} réponses actuelles, {last_count} dernière sauvegarde")
        
        # Sauvegarder à chaque nouvelle réponse
        if current_count > last_count:
            if save_progress():
                st.session_state.last_save_count = current_count
                print(f"💾 Sauvegarde automatique réussie: {current_count} réponses")

def force_save():
    """Force la sauvegarde immédiate"""
    if save_progress():
        current_count = len(st.session_state.get("user_answers", {}))
        st.session_state.last_save_count = current_count
        st.sidebar.success(f"💾 Sauvegarde forcée! ({current_count} réponses)")
        return True
    else:
        st.sidebar.error("❌ Erreur de sauvegarde")
        return False
    
# Configuration pour compatibilité
CHECKPOINT_DIR = "checkpoint"
PROGRESS_FILE = f"{CHECKPOINT_DIR}/user_progress.json"

def ensure_checkpoint_dir():
    """Crée le dossier checkpoint s'il n'existe pas"""
    try:
        Path(CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Erreur création dossier checkpoint: {e}")
        return False

def save_progress():
    """Sauvegarde la progression (compatibilité ancienne fonction)"""
    try:
        ensure_checkpoint_dir()
        
        # Préparer les données
        progress_data = {
            "user_answers": st.session_state.get('user_answers', {}),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Sauvegarder
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Progression sauvegardée: {len(progress_data['user_answers'])} réponses")
        return True
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return False

def load_progress():
    """Charge la progression (compatibilité ancienne fonction)"""
    # Ne pas recharger si déjà en mémoire
    if st.session_state.get('user_answers') and len(st.session_state.user_answers) > 0:
        return st.session_state.user_answers
    
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_answers = data.get('user_answers', {})
            print(f"✅ Progression chargée: {len(user_answers)} réponses")
            return user_answers
        else:
            print("📝 Aucune progression sauvegardée trouvée")
            return {}
            
    except Exception as e:
        print(f"❌ Erreur chargement: {e}")
        return {}

def auto_save():
    """Sauvegarde automatique (compatibilité)"""
    # Éviter les sauvegardes trop fréquentes
    current_count = len(st.session_state.get('user_answers', {}))
    last_saved_count = st.session_state.get('last_auto_save_count', 0)
    
    # Sauvegarder seulement si nouvelle réponse
    if current_count > last_saved_count:
        print(f"🔍 Auto-save: {current_count} réponses actuelles, {last_saved_count} dernière sauvegarde")
        if save_progress():
            st.session_state.last_auto_save_count = current_count
            print(f"💾 Sauvegarde automatique réussie: {current_count} réponses")
    else:
        print(f"⏭️ Auto-save ignoré: pas de nouvelles réponses ({current_count})")

def force_save():
    """Sauvegarde forcée (compatibilité)"""
    return save_progress()