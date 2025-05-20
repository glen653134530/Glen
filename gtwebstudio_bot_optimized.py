
import os
import logging
import datetime
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "8142847766"))

CHOOSING, GET_NAME, GET_EMAIL, GET_PROJECT, CHOOSE_DATE, CHOOSE_TIME = range(6)

DATA_FILE = "rdv_data.csv"

if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Nom", "Email", "Projet", "Date", "Heure", "Timestamp", "UserID"])
    df_init.to_csv(DATA_FILE, index=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📋 Nos Services"), KeyboardButton("📦 Demander un devis")],
        [KeyboardButton("📅 Prendre rendez-vous"), KeyboardButton("✉️ Contacter un humain")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Bienvenue sur GT Web Studio ! Que souhaitez-vous faire aujourd'hui ?",
        reply_markup=reply_markup
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    context.user_data.clear()

    if text == "📋 Nos Services":
        await update.message.reply_text(
            "Nous proposons :\n- Création de sites web\n- Design graphique\n- Gestion réseaux sociaux\n- Développement mobile"
        )
        return CHOOSING
    elif text == "📦 Demander un devis" or text == "📅 Prendre rendez-vous":
        await update.message.reply_text("Quel est votre nom ?")
        return GET_NAME
    elif text == "✉️ Contacter un humain":
        await update.message.reply_text("Veuillez contacter notre support via contact@gtwebstudio.com")
        return CHOOSING
    else:
        await update.message.reply_text("Choix non reconnu. Veuillez utiliser le clavier proposé.")
        return CHOOSING

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nom"] = update.message.text
    await update.message.reply_text("Quel est votre email ?")
    return GET_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if "@" not in email or "." not in email:
        await update.message.reply_text("Email invalide. Veuillez réessayer.")
        return GET_EMAIL
    context.user_data["email"] = email
    await update.message.reply_text("Décrivez brièvement votre projet :")
    return GET_PROJECT

async def get_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["projet"] = update.message.text
    await update.message.reply_text("Quelle date souhaitez-vous ? (format : JJ/MM/AAAA)")
    return CHOOSE_DATE

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    try:
        datetime.datetime.strptime(date, "%d/%m/%Y")
        context.user_data["date"] = date
        await update.message.reply_text("À quelle heure ? (format : HH:MM)")
        return CHOOSE_TIME
    except ValueError:
        await update.message.reply_text("Date invalide. Veuillez respecter le format JJ/MM/AAAA.")
        return CHOOSE_DATE

async def choose_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text
    try:
        datetime.datetime.strptime(time, "%H:%M")
        context.user_data["heure"] = time
        return await save_rdv(update, context)
    except ValueError:
        await update.message.reply_text("Heure invalide. Format attendu : HH:MM.")
        return CHOOSE_TIME

async def save_rdv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = update.effective_user.id

    rdv_entry = {
        "Nom": user_data["nom"],
        "Email": user_data["email"],
        "Projet": user_data["projet"],
        "Date": user_data["date"],
        "Heure": user_data["heure"],
        "Timestamp": timestamp,
        "UserID": user_id,
    }

    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([rdv_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    await context.bot.send_message(chat_id=ADMIN_ID, text=str(rdv_entry))
    await update.message.reply_text("Votre rendez-vous a bien été enregistré. Merci !")
    return CHOOSING

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            GET_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            CHOOSE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_date)],
            CHOOSE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_time)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
