from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Renderはデフォルトでポート10000か、PORT環境変数を使用します
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # メインプロセス終了時に一緒に終了するように設定
    t.start()
