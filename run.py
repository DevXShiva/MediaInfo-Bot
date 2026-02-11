import os
import multiprocessing
from flask import Flask
from bot.main import app as bot_app

# 1. Flask App for Render Health Check
server = Flask(__name__)

@server.route('/')
def health_check():
    return "Bot is Running!", 200

def run_server():
    # Render default PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

def run_bot():
    print("Starting Bot...")
    bot_app.run()

if __name__ == "__main__":
    # Dono kaam ek saath karne ke liye Multiprocessing use kar rahe hain
    p1 = multiprocessing.Process(target=run_server)
    p2 = multiprocessing.Process(target=run_bot)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
