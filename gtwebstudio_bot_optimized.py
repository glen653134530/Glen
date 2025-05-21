
from flask import Flask, request
import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import os
import sqlite3
from datetime import datetime

# Configuration
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8142847766
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Base de données SQLite pour les rendez-vous
DB_NAME = "rendezvous.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nom TEXT,
            projet TEXT,
            datetime TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

keyboard = ReplyKeyboardMarkup([
    ["📋 Nos Services", "📦 Demander un devis"],
    ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]
], resize_keyboard=True)

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur GT Web Studio ! Que souhaitez-vous faire aujourd’hui ?",
        reply_markup=keyboard
    )

# Message handler
user_states = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text

    if text == "📋 Nos Services":
        await update.message.reply_text(
            "Voici nos services disponibles :\n"
            "- Gestion de réseaux sociaux\n"
            "- Création de sites web et apps\n"
            "- Graphisme & Branding\n"
            "- Stratégie digitale personnalisée"
        )

    elif text == "📦 Demander un devis":
        await update.message.reply_text("Veuillez décrire votre projet en quelques lignes.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Un utilisateur (@{update.message.chat.username}) a demandé un devis.")
        user_states[user_id] = "devis"

    elif text == "✉️ Contacter un humain":
        await update.message.reply_text("Un membre de notre équipe vous contactera sous peu.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Un utilisateur (@{update.message.chat.username}) a demandé à parler à un humain.")

    elif text == "📅 Prendre rendez-vous":
        await update.message.reply_text("Merci ! Quel est votre nom ?")
        user_states[user_id] = "rendezvous_nom"

    elif user_id in user_states:
        state = user_states[user_id]

        if state == "rendezvous_nom":
            context.user_data["nom"] = text
            await update.message.reply_text("Quel est le projet concerné ?")
            user_states[user_id] = "rendezvous_projet"

        elif state == "rendezvous_projet":
            context.user_data["projet"] = text
            await update.message.reply_text("Quelle date et heure souhaitez-vous ? (ex: 25 mai à 14h)")
            user_states[user_id] = "rendezvous_datetime"

        elif state == "rendezvous_datetime":
            context.user_data["datetime"] = text
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rendezvous (user_id, nom, projet, datetime, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                context.user_data.get("nom"),
                context.user_data.get("projet"),
                context.user_data.get("datetime"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()

            await update.message.reply_text("Votre rendez-vous a bien été enregistré. Merci !")
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Nouvelle demande de rendez-vous :\nNom : {context.user_data.get('nom')}\nProjet : {context.user_data.get('projet')}\nDate/Heure : {context.user_data.get('datetime')}"
            )
            user_states.pop(user_id)

    else:
        await update.message.reply_text("Merci pour votre message. Utilisez les options du menu ci-dessous :", reply_markup=keyboard)

# App Telegram (Webhook)
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put_nowait(update)
    return "OK"
