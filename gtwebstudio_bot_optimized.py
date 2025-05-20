import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "8142847766"))

CHOOSING, ASSIST_TYPE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📋 Nos Services"), KeyboardButton("📦 Demander un devis")],
        [KeyboardButton("📅 Prendre rendez-vous"), KeyboardButton("✉️ Contacter un humain")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Bienvenue sur GT Web Studio ! Que souhaitez-vous faire aujourd’hui ?",
        reply_markup=reply_markup
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📋 Nos Services":
        await update.message.reply_text("➡️ Services disponibles : Sites Web, Design, Réseaux sociaux, Applications...")
        return CHOOSING

    elif text == "✉️ Contacter un humain":
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton('📦 Problème avec un devis')], [KeyboardButton('⏳ Rendez-vous annulé ou manqué')], [KeyboardButton('💻 J’ai besoin d’un service spécifique')], [KeyboardButton('❓ Autre demande')]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Quel est le sujet de votre demande ?", reply_markup=reply_markup)
        return ASSIST_TYPE

    elif text in ["📦 Demander un devis", "📅 Prendre rendez-vous"]:
        await update.message.reply_text("Merci ! Veuillez nous écrire à contact@gtwebstudio.com ou utiliser le formulaire.")
        return CHOOSING

    else:
        await update.message.reply_text("Commande non reconnue. Veuillez utiliser le menu.")
        return CHOOSING

async def handle_assist_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or f"id:{user.id}"
    full_name = user.full_name
    choice = update.message.text

    await update.message.reply_text("Merci, votre demande a été transmise à notre équipe.")
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="📨 Assistance demandée par @0 (1)\nSujet : 2".format(username, full_name, choice)
    )
    return CHOOSING

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            ASSIST_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_assist_type)],
        },
        fallbacks=[]
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
