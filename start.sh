#!/bin/bash

# Bot ko background mein start karna
python3 -m bot.main &

# Dummy Flask Server (Render health check ke liye)
# Is baar hum heredoc use kar rahe hain taaki syntax error na aaye
python3 << EOF
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def health():
    return 'Bot is Running'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF
