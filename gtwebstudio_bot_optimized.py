from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
import sqlite3
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8142847766

keyboard = ReplyKeyboardMarkup([
    ["📋 Nos Services", "📦 Demander un devis"],
    ["📅 Prendre rendez-vous", "✉️ Contacter un humain"]
], resize_keyboard=True)

DB_NAME = "rendezvous.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rendezvous (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nom TEXT,
            projet TEXT,
            datetime TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
init_db()

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue sur GT Web Studio ! Que souhaitez-vous faire aujourd’hui ?",
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    text = update.message.text
    username = update.message.chat.username or "Utilisateur inconnu"

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
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📦 Demande de devis de @{username}")
        user_states[user_id] = "devis"
    elif text == "✉️ Contacter un humain":
        await update.message.reply_text("Un membre de notre équipe vous contactera sous peu.")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"✉️ Demande de contact humain par @{username}")
    elif text == "📅 Prendre rendez-vous":
        await update.message.reply_text("Quel est votre nom complet ?")
        user_states[user_id] = "rendezvous_nom"
    elif user_id in user_states:
        state = user_states[user_id]
        if state == "rendezvous_nom":
            context.user_data["nom"] = text
            await update.message.reply_text("Quel est le projet concerné ?")
            user_states[user_id] = "rendezvous_projet"
        elif state == "rendezvous_projet":
            context.user_data["projet"] = text
            await update.message.reply_text("À quelle date et heure souhaitez-vous le rendez-vous ?")
            user_states[user_id] = "rendezvous_datetime"
        elif state == "rendezvous_datetime":
            context.user_data["datetime"] = text
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rendezvous (user_id, nom, projet, datetime, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                context.user_data.get("nom"),
                context.user_data.get("projet"),
                context.user_data.get("datetime"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
            await update.message.reply_text("Merci ! Votre rendez-vous a été enregistré.")
            await context.bot.send_message(chat_id=ADMIN_ID, text=
                f"📅 Nouveau rendez-vous\nNom: {context.user_data.get('nom')}\n"
                f"Projet: {context.user_data.get('projet')}\n"
                f"Date/Heure: {context.user_data.get('datetime')}"
            )
            user_states.pop(user_id)
    else:
        await update.message.reply_text("Veuillez choisir une option ci-dessous :", reply_markup=keyboard)

if __name__ == '__main__':
    from telegram.ext import Application
    import asyncio

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # L’URL doit être celle de ton Render suivi de /webhook
    WEBHOOK_URL = "https://glen-oppm.onrender.com/webhook"
    asyncio.run(app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    ))
