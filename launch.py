
import threading
import asyncio
from flask import Flask
from gtwebstudio_bot_optimized import main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot GT Web Studio est actif !"

def start_bot():
    asyncio.run(main())

if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    app.run(host="0.0.0.0", port=10000)
