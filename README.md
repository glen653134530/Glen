# GT Web Studio Telegram Bot

Bot Telegram hébergé gratuitement sur [Render.com](https://render.com)

## Déploiement
1. Crée un compte sur Render
2. Clique sur 'New Web Service' et connecte ce repo GitHub
3. Renseigne `BOT_TOKEN` dans les variables d'environnement
4. Une fois le service en ligne, active le Webhook avec :

```
https://api.telegram.org/bot<TON_TOKEN>/setWebhook?url=https://ton-bot.onrender.com/webhook
```
