# data/process_exam.py
import json
import re
import hashlib
from typing import List, Dict, Tuple
from collections import defaultdict

def normalize_text(text):
    """Normalise le texte pour la comparaison (supprime espaces, ponctuation, casse)"""
    if not text:
        return ""
    # Convertir en minuscules et supprimer les espaces/ponctuation en excès
    normalized = text.lower().strip()
    # Supprimer les espaces multiples
    normalized = ' '.join(normalized.split())
    # Supprimer la ponctuation courante qui peut varier
    chars_to_remove = ['.', ',', ';', ':', '!', '?', '"', "'", '(', ')', '[', ']']
    for char in chars_to_remove:
        normalized = normalized.replace(char, '')
    return normalized

def generate_question_hash(question_text, options):
    """Génère un hash unique basé sur la question et les options"""
    # Normaliser la question
    normalized_question = normalize_text(question_text)
    
    # Normaliser et trier les options pour éviter les différences d'ordre
    normalized_options = []
    if isinstance(options, dict):
        for key in sorted(options.keys()):
            normalized_options.append(normalize_text(options[key]))
    
    # Créer une chaîne unique
    unique_string = normalized_question + '|' + '|'.join(normalized_options)
    
    # Générer un hash MD5
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def find_duplicates(questions):
    """Trouve les questions en double basées sur le contenu"""
    hash_to_questions = defaultdict(list)
    
    for i, question in enumerate(questions):
        question_hash = generate_question_hash(
            question.get('question', ''),
            question.get('options', {})
        )
        hash_to_questions[question_hash].append((i, question))
    
    # Retourner les groupes de doublons
    duplicates = {h: questions_list for h, questions_list in hash_to_questions.items() 
                 if len(questions_list) > 1}
    
    return duplicates

def remove_duplicates_from_questions(questions, theme_name=""):
    """
    Supprime les doublons d'une liste de questions
    
    Args:
        questions: Liste des questions
        theme_name: Nom du thème pour l'affichage
    
    Returns:
        tuple: (questions_uniques, nombre_supprimées)
    """
    if not questions:
        return questions, 0
    
    duplicates = find_duplicates(questions)
    
    if not duplicates:
        return questions, 0
    
    # Indices des questions à supprimer
    indices_to_remove = set()
    
    print(f"🔍 {theme_name}: Trouvé {len(duplicates)} groupes de doublons")
    
    for question_hash, duplicate_group in duplicates.items():
        print(f"   📋 Groupe de {len(duplicate_group)} questions similaires:")
        
        # Afficher un aperçu des questions du groupe
        for idx, (original_idx, question) in enumerate(duplicate_group):
            question_preview = question.get('question', '')[:60] + "..." if len(question.get('question', '')) > 60 else question.get('question', '')
            print(f"      {idx + 1}. [ID orig: {question.get('original_id', 'N/A')}] {question_preview}")
        
        # Stratégie: garder la première, supprimer les autres
        to_keep = duplicate_group[0]
        to_remove = duplicate_group[1:]
        
        print(f"      ✅ Garder: ID original {to_keep[1].get('original_id', 'N/A')}")
        print(f"      ❌ Supprimer: {len(to_remove)} doublons")
        
        # Ajouter les indices à supprimer
        for original_idx, question in to_remove:
            indices_to_remove.add(original_idx)
    
    # Créer la liste finale sans les doublons
    unique_questions = [q for i, q in enumerate(questions) if i not in indices_to_remove]
    
    # Réassigner les IDs séquentiels
    for i, question in enumerate(unique_questions, 1):
        question['id'] = i
    
    removed_count = len(questions) - len(unique_questions)
    if removed_count > 0:
        print(f"   ✨ {theme_name}: {removed_count} doublons supprimés ({len(questions)} → {len(unique_questions)} questions)")
    
    return unique_questions, removed_count

def parse_exam_questions(text_content: str) -> Dict:
    """
    Parse le fichier examen.txt avec détection des questions d'examen blanc
    
    Args:
        text_content: Contenu du fichier examen.txt
        
    Returns:
        Dict contenant les thèmes et leurs questions d'examen
    """
    
    # Nettoyer le texte
    text_content = text_content.strip()
    
    # Pattern pour détecter une question complète d'examen
    question_pattern = r"Question (\d+)\s*\n*Thème\s*:\s*(.*?)\s*\n*Énoncé de la question\s*:\s*(.*?)\s*A\s*-\s*(.*?)\s*B\s*-\s*(.*?)\s*C\s*-\s*(.*?)\s*Réponse attendue\s*:\s*([ABC])"
    
    # Trouver toutes les questions
    questions = re.findall(question_pattern, text_content, re.DOTALL)
    
    # Organiser les questions par thème avec IDs séquentiels
    themes_data = {}
    theme_counters = {}  # Compteur d'ID par thème
    
    for question_match in questions:
        original_question_id, theme_name, question_text, option_a, option_b, option_c, correct_answer = question_match
        
        # Nettoyer le nom du thème
        theme_name = theme_name.strip()
        
        # Initialiser le thème s'il n'existe pas
        if theme_name not in themes_data:
            themes_data[theme_name] = {
                'title': theme_name,
                'questions': []
            }
            theme_counters[theme_name] = 1  # Commencer à 1 pour chaque thème
        
        # Assigner un ID unique séquentiel pour ce thème (temporaire)
        unique_question_id = theme_counters[theme_name]
        theme_counters[theme_name] += 1
        
        # Créer la question avec l'ID unique
        question_data = {
            "id": unique_question_id,
            "original_id": int(original_question_id),  # Garder l'ID original pour référence
            "theme": theme_name,
            "question": question_text.strip(),
            "options": {
                "A": option_a.strip(),
                "B": option_b.strip(),
                "C": option_c.strip()
            },
            "correct_answer": correct_answer.strip(),
            "explanation": ""
        }
        
        themes_data[theme_name]['questions'].append(question_data)
    
    # Supprimer les doublons dans chaque thème
    print("\n🔄 SUPPRESSION DES DOUBLONS PAR THÈME:")
    total_removed = 0
    
    for theme_name, theme_data in themes_data.items():
        original_count = len(theme_data['questions'])
        unique_questions, removed_count = remove_duplicates_from_questions(
            theme_data['questions'], 
            theme_name
        )
        theme_data['questions'] = unique_questions
        total_removed += removed_count
        
        if removed_count == 0:
            print(f"✅ {theme_name}: Aucun doublon trouvé ({original_count} questions)")
    
    if total_removed > 0:
        print(f"\n🎯 RÉSUMÉ: {total_removed} doublons supprimés au total")
    else:
        print(f"\n✨ Aucun doublon détecté dans l'ensemble des questions")
    
    return themes_data

def create_exam_modules(themes_data: Dict) -> List[Dict]:
    """
    Crée la structure des modules d'examen blanc à partir des thèmes détectés
    
    Args:
        themes_data: Données des thèmes avec leurs questions d'examen
        
    Returns:
        Liste des modules formatés pour l'application d'examen blanc
    """
    modules = []
    module_id = 1
    
    for theme_name, theme_data in themes_data.items():
        if not theme_data['questions']:
            print(f"⚠️ Attention: Le thème '{theme_name}' ne contient aucune question valide")
            continue
        
        # Trier les questions par ID
        sorted_questions = sorted(theme_data['questions'], key=lambda x: x['id'])
        
        module = {
            "id": module_id,
            "title": f"Examen - {theme_name}",
            "full_title": theme_name,
            "description": f"{len(sorted_questions)} questions - {theme_name}",
            "theme": theme_name,
            "questions": sorted_questions,
            "total_questions": len(sorted_questions),
            "type": "exam_blanc"  # Identifier comme module d'examen blanc
        }
        modules.append(module)
        module_id += 1
    
    return modules

def create_mixed_exam_module(themes_data: Dict) -> Dict:
    """
    Crée un module d'examen blanc mixte avec toutes les questions mélangées
    
    Args:
        themes_data: Données des thèmes avec leurs questions
        
    Returns:
        Module d'examen blanc mixte
    """
    all_questions = []
    
    # Rassembler toutes les questions
    for theme_name, theme_data in themes_data.items():
        for question in theme_data['questions']:
            # Ajouter l'info du thème à chaque question
            question_copy = question.copy()
            question_copy['original_theme'] = theme_name
            all_questions.append(question_copy)
    
    # Vérifier les doublons inter-thèmes
    print(f"\n🔍 Vérification des doublons entre thèmes...")
    unique_questions, removed_count = remove_duplicates_from_questions(
        all_questions, 
        "Module Mixte"
    )
    
    if removed_count > 0:
        print(f"🎯 {removed_count} doublons inter-thèmes supprimés du module mixte")
    else:
        print(f"✅ Module Mixte: Aucun doublon inter-thème trouvé ({len(unique_questions)} questions)")
    
    # Trier par ID original pour garder un ordre cohérent
    unique_questions.sort(key=lambda x: x.get('original_id', 0))
    
    # Réassigner des IDs séquentiels
    for i, question in enumerate(unique_questions, 1):
        question['id'] = i
    
    mixed_module = {
        "id": 99,  # ID spécial pour l'examen mixte
        "title": "Examen Blanc Complet",
        "full_title": "Examen Blanc - Tous Thèmes",
        "description": f"{len(unique_questions)} questions - Environnement réglementaire + Connaissances techniques",
        "theme": "Mixte",
        "questions": unique_questions,
        "total_questions": len(unique_questions),
        "type": "exam_blanc_complet"
    }
    
    return mixed_module

def validate_exam_questions(themes_data: Dict) -> Tuple[bool, List[str]]:
    """
    Valide la structure des questions d'examen détectées
    
    Returns:
        Tuple (is_valid, errors_list)
    """
    errors = []
    total_questions = 0
    
    expected_themes = ["Environnement réglementaire", "Connaissances techniques"]
    
    for theme_name, theme_data in themes_data.items():
        questions = theme_data['questions']
        
        if not questions:
            errors.append(f"❌ Thème '{theme_name}': Aucune question trouvée")
            continue
        
        total_questions += len(questions)
        
        # Vérifier si le thème est attendu
        if theme_name not in expected_themes:
            errors.append(f"⚠️ Thème inattendu: '{theme_name}' (attendu: {expected_themes})")
        
        # Vérifier chaque question
        for q in questions:
            if not q['question'].strip():
                errors.append(f"❌ Question {q['id']} ({theme_name}): Énoncé vide")
            
            if not all(q['options'].values()):
                errors.append(f"❌ Question {q['id']} ({theme_name}): Options incomplètes")
            
            if q['correct_answer'] not in ['A', 'B', 'C']:
                errors.append(f"❌ Question {q['id']} ({theme_name}): Réponse invalide ({q['correct_answer']})")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        print(f"✅ Validation réussie: {total_questions} questions d'examen dans {len(themes_data)} thèmes")
        print(f"🔄 IDs automatiquement réassignés pour éviter les doublons")
    
    return is_valid, errors

def display_exam_summary(themes_data: Dict):
    """
    Affiche un résumé de la conversion des questions d'examen
    """
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA CONVERSION - EXAMEN BLANC")
    print("="*70)
    
    total_questions = sum(len(theme_data['questions']) for theme_data in themes_data.values())
    print(f"📚 Nombre de thèmes d'examen: {len(themes_data)}")
    print(f"❓ Nombre total de questions: {total_questions}")
    
    print(f"\n📋 DÉTAIL PAR THÈME D'EXAMEN:")
    for theme_name, theme_data in themes_data.items():
        num_questions = len(theme_data['questions'])
        print(f"   • {theme_name}: {num_questions:3d} questions")
        
        # Afficher les IDs réassignés et originaux pour vérification
        if num_questions <= 10:
            for q in theme_data['questions']:
                print(f"     ID {q['id']} (original: {q['original_id']})")
        else:
            first_5 = theme_data['questions'][:5]
            last_5 = theme_data['questions'][-5:]
            print(f"     Premiers: " + ", ".join([f"ID {q['id']}(orig:{q['original_id']})" for q in first_5]))
            print(f"     Derniers: " + ", ".join([f"ID {q['id']}(orig:{q['original_id']})" for q in last_5]))
            print(f"     Total: {num_questions} questions avec IDs séquentiels 1-{num_questions}")
    
    print(f"\n💡 Note: Les IDs ont été automatiquement réassignés pour éviter les doublons")
    print(f"   Les IDs originaux sont conservés dans le champ 'original_id'")
    print(f"🧹 Suppression automatique des doublons activée")
    print("\n" + "="*70)

# Script principal pour les examens blancs
if __name__ == "__main__":
    print("🎯 Démarrage de la conversion des questions d'examen blanc...")
    print("🧹 Suppression automatique des doublons activée")
    
    # Lire le fichier d'examen
    try:
        with open("examen.txt", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Erreur: Fichier 'examen.txt' non trouvé!")
        print("📝 Veuillez créer le fichier 'examen.txt' avec vos questions d'examen.")
        print("\nFormat attendu:")
        print("Question X")
        print("Thème : Nom du thème")
        print("Énoncé de la question : ...")
        print("A - Option A")
        print("B - Option B") 
        print("C - Option C")
        print("Réponse attendue : A/B/C")
        exit(1)
    except UnicodeDecodeError:
        print("❌ Erreur d'encodage. Essayons avec 'latin-1'...")
        try:
            with open("examen.txt", "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Impossible de lire le fichier: {e}")
            exit(1)
    
    print("📖 Fichier examen.txt lu avec succès!")
    
    # Parser les questions d'examen (avec suppression des doublons)
    print("🔍 Analyse des questions d'examen blanc...")
    themes_data = parse_exam_questions(content)
    
    if not themes_data:
        print("❌ Aucune question d'examen détectée! Vérifiez le format de votre fichier.")
        print("\nFormat attendu:")
        print("Question 1")
        print("Thème : Environnement réglementaire")
        print("Énoncé de la question : ...")
        print("A - Option A")
        print("B - Option B")
        print("C - Option C")
        print("Réponse attendue : A")
        exit(1)
    
    # Validation
    print("✔️  Validation des questions d'examen...")
    is_valid, errors = validate_exam_questions(themes_data)
    
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
    
    # Créer les modules d'examen
    print("🏗️  Création de la structure des modules d'examen...")
    exam_modules = create_exam_modules(themes_data)
    
    # Optionnel : Créer le module d'examen mixte (décommentez si souhaité)
    # print("🎯 Création du module d'examen blanc complet...")
    # mixed_exam = create_mixed_exam_module(themes_data)
    # exam_modules.append(mixed_exam)
    
    # Créer la structure de données finale pour les examens
    total_questions = sum(len(theme_data['questions']) for theme_data in themes_data.values())
    exam_data = {
        "metadata": {
            "total_questions": total_questions,
            "total_modules": len(exam_modules),
            "created_date": "2025-05-23",
            "source_file": "examen.txt",
            "type": "exam_blanc",
            "deduplication": True,  # Nouvelle métadonnée
            "themes": {
                theme_name: {
                    "title": theme_name,
                    "question_count": len(theme_data['questions'])
                }
                for theme_name, theme_data in themes_data.items()
            }
        },
        "modules": exam_modules
    }
    
    # Sauvegarder en JSON
    output_file = "exam_questions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(exam_data, f, ensure_ascii=False, indent=2)
    
    # Afficher le résumé
    display_exam_summary(themes_data)
    
    print(f"💾 Fichier sauvegardé: {output_file}")
    print("🎉 Conversion des questions d'examen terminée avec succès!")
    
    # Instructions pour la suite
    print(f"\n📋 PROCHAINES ÉTAPES:")
    print(f"1. Vérifiez le fichier '{output_file}' généré")
    print(f"2. Intégrez le mode examen blanc dans votre application")
    print(f"3. Testez vos {total_questions} questions d'examen réparties en {len(exam_modules)} modules!")
    print(f"🧹 4. Les doublons ont été automatiquement supprimés")
    print(f"💡 Note: Le module mixte est désactivé. Décommentez les lignes pour l'activer.")