# 🧠 Plateforme d'Entraînement AMF

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

Plateforme d'entraînement **non officielle**, **open-source** et **gratuite** pour préparer la certification AMF (Autorité des Marchés Financiers).

## 🎯 Fonctionnalités

- **560 questions** réparties en 12 modules thématiques
- **10 examens blancs** avec sélection aléatoire de questions
- **Mode révision** pour retravailler les erreurs
- **Sauvegarde automatique** de la progression
- **Interface moderne** et responsive avec Streamlit
- **Statistiques détaillées** de performance par module

## 🚀 Installation locale et utilisation

1. **Cloner le repository**
```bash
git clone https://github.com/velerl/plateforme-entrainement-AMF.git
cd entrainement-amf
```

2. **Créer un environnement virtuel** (recommandé)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`


## 📚 Structure des modules

1. **M1** - Cadre institutionnel et réglementaire européen
2. **M2** - Cadre réglementaire des prestataires
3. **M3** - Règles de bonne conduite et organisation déontologique
4. **M4** - Les instruments financiers et crypto-actifs
5. **M5** - Les émissions et les opérations sur titres
6. **M6** - La gestion collective / La gestion sous mandat
7. **M7** - Le fonctionnement et l'organisation des marchés
8. **M8** - Le post-marché
9. **M9** - Les bases comptables et financières
10. **M10** - Démarchage bancaire et financier - Vente à distance - Conseil
11. **M11** - Relations avec les clients, lutte anti-blanchiment
12. **M12** - La relation client dans un environnement numérique

## 🎓 Examens blancs

- **2 parties** : Environnement réglementaire (56 questions) et Connaissances techniques (64 questions)
- **Durée indicative** : 2 heures
- **Seuil de réussite** : 80% minimum dans chaque partie
- **10 examens** avec sélection aléatoire des questions

## 💾 Sauvegarde de la progression

Votre progression est automatiquement sauvegardée localement dans le dossier `checkpoint/`. Vous pouvez :
- Reprendre où vous vous êtes arrêté
- Réinitialiser votre progression par module
- Réinitialiser complètement votre progression

## 🛠️ Technologies utilisées

- **[Streamlit](https://streamlit.io/)** - Framework pour l'interface web
- **[Plotly](https://plotly.com/)** - Visualisations interactives
- **Python 3.8+** - Langage de programmation

## 📝 Licence

Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Avertissement

Cette plateforme est un outil d'entraînement **non officiel** créé pour aider à la préparation de la certification AMF. Elle ne remplace pas la formation officielle et n'est pas affiliée à l'AMF.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Suggérer des améliorations
- 🔧 Proposer des pull requests

## 📧 Contact

Pour toute question ou suggestion, ouvrez une [issue](https://github.com/velerl/plateforme-entrainement-amf/issues) sur GitHub.

---

**Bon entraînement et bonne chance pour votre certification AMF ! 🎯**
