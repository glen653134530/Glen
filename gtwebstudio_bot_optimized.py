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
    lignes = ["{} : {}".format(k, v) for k, v in row.items()]
    text = "\n".join(lignes)
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📅 Nouveau RDV :\n{text}")
    return CHOOSING

async def handle_assist_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.username or f"id:{user.id}"
    full_name = user.full_name
    choice = update.message.text
    await update.message.reply_text("Merci, votre demande a été transmise.")
    msg = f"📨 Assistance de @{username} ({full_name})\nSujet : {choice}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return CHOOSING

def main():
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
    app.run_polling()

# Lancement Render (Flask + bot)
if name == "__main__":
    bot_thread = threading.Thread(target=main)
    bot_thread.start()

    app = Flask(__name__)

    @app.route("/")
    def home():
        return "Bot GT Web Studio est en ligne !"

    app.run(host='0.0.0.0', port=10000)
