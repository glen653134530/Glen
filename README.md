# GT Web Studio Bot – Déploiement Render

Ce dépôt contient le bot Telegram de GT Web Studio, prêt à être déployé sur [Render](https://render.com).

## Fonctionnalités
- Menu interactif Telegram
- Prise de rendez-vous avec validation
- Enregistrement CSV
- Notification automatique à l’admin Telegram

## Déploiement sur Render (plan gratuit)

1. Crée un compte sur https://render.com
2. Clique sur "New + > Web Service"
3. Sélectionne "Connect a repository"
4. Choisis ce dépôt GitHub
5. Configure :
   - Type: **Background Worker**
   - Start command: `python3 gtwebstudio_bot_optimized.py`
   - Runtime: Python 3
   - Build command: `pip install -r requirements.txt`

6. Dans "Environment", ajoute les variables suivantes :
   - `TELEGRAM_BOT_TOKEN` = Ton token Telegram
   - `TELEGRAM_ADMIN_ID` = Ton ID Telegram

7. Clique sur "Deploy Service"

Et ton bot sera actif en arrière-plan 24h/24 sur Telegram.