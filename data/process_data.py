# data/process_data.py
import json
import re
from typing import List, Dict, Tuple

def parse_questions_by_theme(text_content: str) -> Dict:
    """
    Parse le fichier avec détection automatique des thèmes et questions
    
    Args:
        text_content: Contenu du fichier questions.txt
        
    Returns:
        Dict contenant les thèmes et leurs questions
    """
    
    # Nettoyer le texte
    text_content = text_content.strip()
    
    # Pattern pour détecter les thèmes
    theme_pattern = r"Thème (\d+)\s*:\s*(.+?)(?=\n|$)"
    
    # Pattern pour détecter les questions complètes
    question_pattern = r"Question (\d+)\s*\n*Énoncé de la question \d+\s*:\s*(.*?)\s*A\s*-\s*(.*?)\s*B\s*-\s*(.*?)\s*C\s*-\s*(.*?)\s*Réponse attendue\s*:\s*([ABC])"
    
    themes = {}
    current_theme = None
    current_theme_title = None
    
    # Diviser le texte en sections par thème
    lines = text_content.split('\n')
    current_section = []
    
    for line in lines:
        line = line.strip()
        
        # Détecter un nouveau thème
        theme_match = re.match(theme_pattern, line)
        if theme_match:
            # Sauvegarder le thème précédent s'il existe
            if current_theme is not None and current_section:
                section_text = '\n'.join(current_section)
                themes[current_theme] = {
                    'title': current_theme_title,
                    'content': section_text,
                    'questions': []
                }
            
            # Initialiser le nouveau thème
            current_theme = int(theme_match.group(1))
            current_theme_title = theme_match.group(2).strip()
            current_section = []
        else:
            # Ajouter la ligne à la section actuelle
            if line:  # Ignorer les lignes vides
                current_section.append(line)
    
    # Sauvegarder le dernier thème
    if current_theme is not None and current_section:
        section_text = '\n'.join(current_section)
        themes[current_theme] = {
            'title': current_theme_title,
            'content': section_text,
            'questions': []
        }
    
    # Parser les questions pour chaque thème
    for theme_id, theme_data in themes.items():
        content = theme_data['content']
        
        # Trouver toutes les questions dans ce thème
        questions = re.findall(question_pattern, content, re.DOTALL)
        
        parsed_questions = []
        for question_match in questions:
            question_id, question_text, option_a, option_b, option_c, correct_answer = question_match
            
            question_data = {
                "id": int(question_id),
                "theme_id": theme_id,
                "question": question_text.strip(),
                "options": {
                    "A": option_a.strip(),
                    "B": option_b.strip(),
                    "C": option_c.strip()
                },
                "correct_answer": correct_answer.strip(),
                "explanation": ""
            }
            parsed_questions.append(question_data)
        
        theme_data['questions'] = parsed_questions
    
    return themes

def create_modules_from_themes(themes_data: Dict) -> List[Dict]:
    """
    Crée la structure des modules à partir des thèmes détectés
    
    Args:
        themes_data: Données des thèmes avec leurs questions
        
    Returns:
        Liste des modules formatés pour l'application
    """
    modules = []
    
    for theme_id in sorted(themes_data.keys()):
        theme = themes_data[theme_id]
        
        if not theme['questions']:
            print(f"⚠️ Attention: {theme['title']} ne contient aucune question valide")
            continue
        
        module = {
            "id": theme_id,
            "title": f"Thème {theme_id}",
            "full_title": theme['title'],
            "description": f"{len(theme['questions'])} questions - {theme['title'][:50]}{'...' if len(theme['title']) > 50 else ''}",
            "questions": theme['questions'],
            "total_questions": len(theme['questions'])
        }
        modules.append(module)
    
    return modules

def validate_questions(themes_data: Dict) -> Tuple[bool, List[str]]:
    """
    Valide la structure des questions détectées
    
    Returns:
        Tuple (is_valid, errors_list)
    """
    errors = []
    total_questions = 0
    
    for theme_id, theme in themes_data.items():
        theme_title = theme['title']
        questions = theme['questions']
        
        if not questions:
            errors.append(f"❌ Thème {theme_id} ({theme_title}): Aucune question trouvée")
            continue
        
        total_questions += len(questions)
        
        # Vérifier chaque question
        for q in questions:
            if not q['question'].strip():
                errors.append(f"❌ Question {q['id']}: Énoncé vide")
            
            if not all(q['options'].values()):
                errors.append(f"❌ Question {q['id']}: Options incomplètes")
            
            if q['correct_answer'] not in ['A', 'B', 'C']:
                errors.append(f"❌ Question {q['id']}: Réponse invalide ({q['correct_answer']})")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        print(f"✅ Validation réussie: {total_questions} questions dans {len(themes_data)} thèmes")
    
    return is_valid, errors

def display_summary(themes_data: Dict):
    """
    Affiche un résumé de la conversion
    """
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA CONVERSION")
    print("="*60)
    
    total_questions = sum(len(theme['questions']) for theme in themes_data.values())
    print(f"📚 Nombre total de thèmes: {len(themes_data)}")
    print(f"❓ Nombre total de questions: {total_questions}")
    
    print(f"\n📋 DÉTAIL PAR THÈME:")
    for theme_id in sorted(themes_data.keys()):
        theme = themes_data[theme_id]
        num_questions = len(theme['questions'])
        title = theme['title'][:60] + "..." if len(theme['title']) > 60 else theme['title']
        print(f"   Thème {theme_id:2d}: {num_questions:3d} questions - {title}")
    
    print("\n" + "="*60)

# Exemple d'utilisation et script principal
if __name__ == "__main__":
    print("🚀 Démarrage de la conversion des questions par thème...")
    
    # Lire le fichier de questions
    try:
        with open("questions.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Erreur: Fichier 'questions.txt' non trouvé!")
        print("📝 Veuillez créer le fichier 'questions.txt' avec vos questions.")
        exit(1)
    except UnicodeDecodeError:
        print("❌ Erreur d'encodage. Essayons avec 'latin-1'...")
        try:
            with open("questions.txt", "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Impossible de lire le fichier: {e}")
            exit(1)
    
    print("📖 Fichier lu avec succès!")
    
    # Parser les thèmes et questions
    print("🔍 Analyse des thèmes et questions...")
    themes_data = parse_questions_by_theme(content)
    
    if not themes_data:
        print("❌ Aucun thème détecté! Vérifiez le format de votre fichier.")
        print("Format attendu:")
        print("Thème X : Titre du thème")
        print("Question Y")
        print("Énoncé de la question Y :")
        print("...")
        exit(1)
    
    # Validation
    print("✔️  Validation des données...")
    is_valid, errors = validate_questions(themes_data)
    
    if not is_valid:
        print("❌ Erreurs détectées:")
        for error in errors[:10]:  # Limiter à 10 erreurs
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... et {len(errors) - 10} autres erreurs")
        
        print("\n🤔 Voulez-vous continuer malgré les erreurs? (o/n)")
        response = input().lower()
        if response != 'o':
            exit(1)
    
    # Créer les modules
    print("🏗️  Création de la structure des modules...")
    modules = create_modules_from_themes(themes_data)
    
    # Créer la structure de données finale
    total_questions = sum(len(theme['questions']) for theme in themes_data.values())
    data = {
        "metadata": {
            "total_questions": total_questions,
            "total_modules": len(modules),
            "created_date": "2025-05-22",
            "source_file": "questions.txt",
            "themes": {
                str(theme_id): {
                    "title": theme['title'],
                    "question_count": len(theme['questions'])
                }
                for theme_id, theme in themes_data.items()
            }
        },
        "modules": modules
    }
    
    # Sauvegarder en JSON
    output_file = "questions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Afficher le résumé
    display_summary(themes_data)
    
    print(f"💾 Fichier sauvegardé: {output_file}")
    print("🎉 Conversion terminée avec succès!")
    
    # Instructions pour la suite
    print(f"\n📋 PROCHAINES ÉTAPES:")
    print(f"1. Vérifiez le fichier '{output_file}' généré")
    print(f"2. Lancez l'application: streamlit run app.py")
    print(f"3. Testez vos {total_questions} questions réparties en {len(modules)} thèmes!")