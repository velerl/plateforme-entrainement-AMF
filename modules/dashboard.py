import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.utils import get_user_progress, calculate_score, get_performance_level

def show_enhanced_dashboard(data):
    """Affiche le tableau de bord principal"""
    st.header("📊 Tableau de bord")
    
    # Métriques principales avec style amélioré
    col1, col2, col3, col4 = st.columns(4)
    
    answered, total = get_user_progress(data)
    completion_rate = (answered / total) * 100 if total > 0 else 0
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📚</h3>
            <h2 style="color: var(--primary-color);">{}</h2>
            <p>Modules disponibles</p>
        </div>
        """.format(len(data['modules'])), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>❓</h3>
            <h2 style="color: var(--info-color);">{}</h2>
            <p>Questions totales</p>
        </div>
        """.format(data['metadata']['total_questions']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>✅</h3>
            <h2 style="color: var(--success-color);">{}</h2>
            <p>Questions répondues</p>
        </div>
        """.format(answered), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📈</h3>
            <h2 style="color: var(--warning-color);">{:.1f}%</h2>
            <p>Avancement</p>
        </div>
        """.format(completion_rate), unsafe_allow_html=True)
    

    # Graphique de progression global
    if answered > 0:
        st.markdown("<br>", unsafe_allow_html=True)  # Petit espace avant le titre
        st.subheader("📈 Progression par module")
        
        module_data = []
        for module in data['modules']:
            correct, total_answered = calculate_score(module['questions'], st.session_state.user_answers, module['id'])
            progress_pct = (total_answered / module['total_questions']) * 100
            score_pct = (correct / total_answered * 100) if total_answered > 0 else 0
            
            # Déterminer la couleur selon le score
            if score_pct >= 80:
                color = '#28a745'  # Vert pour excellent
                status = 'Excellent'
            elif score_pct >= 60:
                color = '#ffc107'  # Jaune pour correct
                status = 'Correct'
            elif total_answered > 0:
                color = '#dc3545'  # Rouge pour à améliorer
                status = 'À améliorer'
            else:
                color = '#6c757d'  # Gris pour non commencé
                status = 'Non commencé'
            
            module_data.append({
                'Module': f"M{module['id']}",
                'Nom': module['title'],
                'Progression': progress_pct,
                'Restant': 100 - progress_pct,
                'Score': score_pct,
                'Couleur': color,
                'Questions': f"{total_answered}/{module['total_questions']}",
                'Statut': status
            })
        
        df = pd.DataFrame(module_data)
        
        # Graphique en barres optimisé
        fig = go.Figure()
        
        # Barre de progression avec couleurs selon le score
        fig.add_trace(go.Bar(
            name='Progression',
            x=df['Module'],
            y=df['Progression'],
            marker_color=df['Couleur'],
            text=[f"{prog:.0f}%<br>{questions}" if prog > 8 else f"{prog:.0f}%" if prog > 0 else "" 
                  for prog, questions in zip(df['Progression'], df['Questions'])],
            textposition='inside',
            textfont=dict(color='white', size=12, family="Arial"),
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Progression: %{y:.1f}%<br>' +
                         'Questions: %{customdata[1]}<br>' +
                         'Score: %{customdata[2]:.1f}%<br>' +
                         'Statut: %{customdata[3]}<br>' +
                         '<extra></extra>',
            customdata=list(zip(df['Nom'], df['Questions'], df['Score'], df['Statut'])),
            showlegend=False
        ))
        
        # Barre restante avec style subtil
        fig.add_trace(go.Bar(
            name='Restant',
            x=df['Module'],
            y=df['Restant'],
            marker_color='rgba(108, 117, 125, 0.15)',
            marker_line_color='rgba(108, 117, 125, 0.3)',
            marker_line_width=1,
            text=['Non commencé' if rest == 100 else '' for rest in df['Restant']],
            textposition='inside',
            textfont=dict(color='#6c757d', size=11),
            hovertemplate='<b>%{customdata}</b><br>' +
                         'Restant: %{y:.1f}%<br>' +
                         '<extra></extra>',
            customdata=df['Nom'],
            showlegend=False
        ))
        
        # Layout optimisé sans légendes d'axes
        fig.update_layout(
            barmode='stack',
            xaxis={
                'showgrid': False,
                'zeroline': False,
                'showline': False,
                'ticks': '',
                'showticklabels': True,
                'tickfont': {'size': 13, 'color': '#2c3e50', 'family': 'Arial'},
                'title': None
            },
            yaxis={
                'showgrid': True,
                'gridcolor': 'rgba(0,0,0,0.05)',
                'gridwidth': 1,
                'zeroline': False,
                'showline': False,
                'ticks': '',
                'showticklabels': False,
                'range': [0, 100],
                'title': None
            },
            template="plotly_white",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Arial', 'color': '#2c3e50'},
            showlegend=False,
            margin=dict(t=20, b=10, l=20, r=20),
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Légende des couleurs simplifiée et élégante
        st.markdown("""
        <div style="display: flex; justify-content: center; gap: 30px; margin-top: 5px; font-size: 14px;">
            <span style="display: flex; align-items: center;">
                <span style="width: 16px; height: 16px; background-color: #28a745; border-radius: 3px; margin-right: 8px;"></span>
                <strong>Excellent (≥80%)</strong>
            </span>
            <span style="display: flex; align-items: center;">
                <span style="width: 16px; height: 16px; background-color: #ffc107; border-radius: 3px; margin-right: 8px;"></span>
                <strong>Correct (60-79%)</strong>
            </span>
            <span style="display: flex; align-items: center;">
                <span style="width: 16px; height: 16px; background-color: #dc3545; border-radius: 3px; margin-right: 8px;"></span>
                <strong>À améliorer (&lt;60%)</strong>
            </span>
            <span style="display: flex; align-items: center;">
                <span style="width: 16px; height: 16px; background-color: #6c757d; border-radius: 3px; margin-right: 8px;"></span>
                <strong>Non commencé</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Aperçu des modules avec style amélioré
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗂️ Aperçu détaillé des modules")
    
    for i, module in enumerate(data['modules']):
        correct, total_answered = calculate_score(module['questions'], st.session_state.user_answers, module['id'])
        progress_pct = (total_answered / module['total_questions']) * 100
        
        with st.expander(f"📝 {module['title']} - {module['full_title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Questions totales:** {module['total_questions']}")
                st.write(f"**Questions répondues:** {total_answered}")
                st.write(f"**Progression:** {progress_pct:.1f}%")
                
                if total_answered > 0:
                    score_pct = (correct / total_answered) * 100
                    level, level_type = get_performance_level(score_pct)
                    st.write(f"**Score:** {score_pct:.1f}% - {level}")
                else:
                    st.write("**Score:** Non commencé")
                
                # Barre de progression du module
                st.progress(progress_pct / 100)
            
            with col2:
                if st.button(f"🎯 Commencer {module['title']}", key=f"start_{i}"):
                    st.session_state.current_module = module
                    st.session_state.current_question_idx = 0
                    st.session_state.quiz_started = True
                    st.session_state.quiz_completed = False
                    st.session_state.start_time = datetime.now()
                    st.session_state.quiz_mode = 'practice'
                    # Nettoyer les données d'examen blanc
                    st.session_state.exam_blanc_questions = None
                    st.session_state.current_exam_blanc_id = None
                    st.rerun()
    
    # Section Examen Blanc optimisée
    st.subheader("🎓 Examens blancs disponibles")
    st.info("💡 Chaque examen blanc propose une sélection aléatoire différente de questions pour varier vos entraînements.")
    
    # Fonction helper pour créer un examen blanc
    def create_exam_card(exam_num):
        """Crée une carte d'examen blanc avec barre de progression intégrée"""
        
        # Calculer la progression pour cet examen
        seed_to_use = exam_num
        if 'exam_seed_mapping' in st.session_state:
            seed_to_use = st.session_state.exam_seed_mapping.get(exam_num, exam_num)
        
        answered_count = sum(1 for key in st.session_state.user_answers.keys() 
                           if key.startswith(f'exam{seed_to_use}_'))
        
        progress_pct = (answered_count / 120) * 100  # 120 questions par examen
        
        with st.container():
            # Carte complète avec barre de progression intégrée
            st.markdown(f"""
            <div class="module-card">
                <h4>🎓 Examen Blanc #{exam_num}</h4>
                <p><strong>Structure:</strong></p>
                <p>📋 Partie 1: 56 questions (Env. réglementaire)</p>
                <p>🔧 Partie 2: 64 questions (Conn. techniques)</p>
                <p><strong>Durée:</strong> 2h (indicatif)</p>
                <p><strong>Seuil:</strong> ≥80% dans chaque partie</p>
                <p style="font-size: 0.9em; color: var(--text-secondary);">Questions sélectionnées aléatoirement</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Barre de progression séparée
            st.markdown(f"""
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="font-size: 0.9em; font-weight: bold;">Progression:</span>
                    <span style="font-size: 0.9em; font-weight: bold;">{progress_pct:.1f}%</span>
                </div>
                <div style="background: rgba(108, 117, 125, 0.2); border-radius: 10px; overflow: hidden; height: 8px;">
                    <div style="background: #28a745; width: {progress_pct}%; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                </div>
                <div style="text-align: center; font-size: 0.8em; margin-top: 5px; opacity: 0.7;">
                    {answered_count}/120 questions répondues
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Boutons côte à côte
            col_start, col_regen = st.columns([3, 1])
            
            with col_start:
                if st.button(f"🚀 Commencer l'Examen #{exam_num}", 
                           key=f"exam_blanc_{exam_num}", 
                           type="primary", 
                           use_container_width=True):
                    from modules.exam_blanc import create_exam_blanc
                    
                    print(f"DEBUG: Lancement examen #{exam_num} avec seed {seed_to_use}")
                    
                    # Créer l'examen avec le bon seed
                    exam_questions = create_exam_blanc(exam_id=seed_to_use)
                    if exam_questions:
                        st.session_state.exam_blanc_questions = exam_questions
                        st.session_state.current_exam_blanc_id = exam_num
                        st.session_state.current_module = None
                        st.session_state.current_question_idx = 0
                        st.session_state.quiz_started = True
                        st.session_state.quiz_completed = False
                        st.session_state.start_time = datetime.now()
                        st.session_state.exam_blanc_part = 1
                        st.session_state.quiz_mode = 'exam_blanc'
                        st.rerun()
                    else:
                        st.error("❌ Impossible de créer l'examen blanc. Vérifiez que le fichier exam_questions.json existe.")
            
            with col_regen:
                if st.button(f"🔄", 
                           key=f"regenerate_{exam_num}", 
                           type="secondary", 
                           use_container_width=True,
                           help=f"Régénérer l'examen #{exam_num} avec de nouvelles questions"):
                    # Régénérer l'examen avec de nouvelles questions aléatoires
                    if st.session_state.get(f'confirm_regenerate_{exam_num}', False):
                        from modules.exam_blanc import create_exam_blanc
                        import random as rnd
                        
                        # Générer un seed complètement aléatoire pour de nouvelles questions
                        new_seed = rnd.randint(10000, 99999)
                        print(f"DEBUG: Régénération examen #{exam_num} avec seed {new_seed}")
                        
                        new_exam = create_exam_blanc(exam_id=new_seed)
                        
                        if new_exam:
                            # Créer un mapping pour que l'examen #X utilise le nouveau seed
                            if 'exam_seed_mapping' not in st.session_state:
                                st.session_state.exam_seed_mapping = {}
                            
                            # Supprimer les anciennes réponses avec l'ancien préfixe
                            old_seed = st.session_state.exam_seed_mapping.get(exam_num, exam_num)
                            keys_to_remove = []
                            for key in st.session_state.user_answers.keys():
                                if key.startswith(f'exam{old_seed}_'):
                                    keys_to_remove.append(key)
                            
                            for key in keys_to_remove:
                                del st.session_state.user_answers[key]
                            
                            # Mettre à jour le mapping
                            st.session_state.exam_seed_mapping[exam_num] = new_seed
                            
                            # Si c'est l'examen actuellement chargé, le remplacer
                            if st.session_state.get('current_exam_blanc_id') == exam_num:
                                st.session_state.exam_blanc_questions = new_exam
                                st.session_state.exam_blanc_part = 1
                                st.session_state.current_question_idx = 0
                            
                            # Sauvegarder les changements
                            from modules.persistence import save_user_progress
                            save_user_progress(force_save=True)
                            
                            st.session_state[f'confirm_regenerate_{exam_num}'] = False
                            st.success(f"✅ Examen blanc #{exam_num} régénéré avec de nouvelles questions! (Seed: {new_seed})")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la régénération")
                    else:
                        st.session_state[f'confirm_regenerate_{exam_num}'] = True
                        st.warning(f"⚠️ Régénérer l'examen #{exam_num} avec de nouvelles questions ? Cela supprimera vos réponses actuelles.")
    
    # Créer une grille d'examens blancs - 2 par ligne
    exam_numbers = list(range(1, 11))  # 10 examens blancs
    
    for i in range(0, len(exam_numbers), 2):  # Traiter par paires
        col1, col2 = st.columns(2)
        
        # Premier examen de la paire
        with col1:
            create_exam_card(exam_numbers[i])
        
        # Deuxième examen de la paire (s'il existe)
        with col2:
            if i + 1 < len(exam_numbers):
                create_exam_card(exam_numbers[i + 1])
            else:
                # Colonne vide si nombre impair d'examens
                st.empty()