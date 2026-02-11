#!/bin/bash

# Bot start karna (background mein)
python3 -m bot.main &

# Dummy Flask server (Render port check pass karne ke liye)
# Render default PORT environment variable deta hai
python3 -c "from flask import Flask; app = Flask(__name__); @app.route('/')\
def health(): return 'Bot is Running'; app.run(host='0.0.0.0', port=$PORT)"
