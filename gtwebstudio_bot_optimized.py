
import os
import logging
import datetime
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "8142847766"))
DATA_FILE = "rdv_data.csv"

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Nom", "Email", "Projet", "Date", "Heure", "Timestamp", "UserID"]).to_csv(DATA_FILE, index=False)

CHOOSING, GET_NAME, GET_EMAIL, GET_PROJECT, CHOOSE_DATE, CHOOSE_TIME, ASSIST_TYPE = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📋 Nos Services"), KeyboardButton("📦 Demander un devis")],
        [KeyboardButton("📅 Prendre rendez-vous"), KeyboardButton("✉️ Contacter un humain")]
    ]
    await update.message.reply_text(
        "Bienvenue sur GT Web Studio ! Que souhaitez-vous faire aujourd’hui ?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📋 Nos Services":
    services = (
        "📱 Applications mobiles\n"
        "🌐 Création de sites web\n"
        "✒️ Design graphique\n"
        "📣 Gestion des réseaux sociaux\n"
        "☁️ Hébergement & nom de domaine\n"
        "✍️ Rédaction de contenu & storytelling"
    )
    await update.message.reply_text("Voici nos services :\n" + services)
    return CHOOSING
    elif text == "📦 Demander un devis":
        await update.message.reply_text("Merci ! Veuillez préciser votre projet :")
        return GET_PROJECT
    elif text == "📅 Prendre rendez-vous":
        await update.message.reply_text("Quel est votre nom ?")
        return GET_NAME
    elif text == "✉️ Contacter un humain":
        reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton("📦 Problème avec un devis")],
            [KeyboardButton("⏳ Rendez-vous annulé ou manqué")],
            [KeyboardButton("💻 J’ai besoin d’un service spécifique")],
            [KeyboardButton("❓ Autre demande")]
        ], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Quel est le sujet de votre demande ?", reply_markup=reply_markup)
        return ASSIST_TYPE
    else:
        await update.message.reply_text("Commande non reconnue. Veuillez utiliser le menu.")
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
    await update.message.reply_text("Décrivez votre projet :")
    return GET_PROJECT

async def get_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["projet"] = update.message.text
    await update.message.reply_text("Quelle date ? (JJ/MM/AAAA)")
    return CHOOSE_DATE

async def choose_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text
    try:
        datetime.datetime.strptime(date, "%d/%m/%Y")
        context.user_data["date"] = date
        await update.message.reply_text("À quelle heure ? (HH:MM)")
        return CHOOSE_TIME
    except ValueError:
        await update.message.reply_text("Format invalide. Reprenez au format JJ/MM/AAAA.")
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
    row = {
        "Nom": user_data["nom"],
        "Email": user_data["email"],
        "Projet": user_data["projet"],
        "Date": user_data["date"],
        "Heure": user_data["heure"],
        "Timestamp": timestamp,
        "UserID": user_id
    }
    df = pd.read_csv(DATA_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    await update.message.reply_text("Rendez-vous enregistré. Merci !")
    lines = ["{} : {}".format(k, v) for k, v in row.items()]
    await context.bot.send_message(chat_id=ADMIN_ID, text="
".join(lines))
    return CHOOSING

async def handle_assist_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or f"id:{user.id}"
    full_name = user.full_name
    sujet = update.message.text
    msg = f"📨 Assistance de @{username} ({full_name})
Sujet : {sujet}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("Merci, votre demande a été transmise.")
    return CHOOSING

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            GET_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project)],
            CHOOSE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_date)],
            CHOOSE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_time)],
            ASSIST_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_assist_type)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    await app.run_polling()
