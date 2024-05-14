from flask import Flask, request, jsonify
from ultrabot import ultraChatBot
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    if request.method == 'POST':
        data = request.get_json()
        if data and 'data' in data:
            messages = data['data']
            for message in messages:
                if 'from' in message and 'body' in message:
                    chat_id = message['from']
                    bot = ultraChatBot(data)
                    bot.handle_conversation(chat_id, message)
        return 'OK', 200

if __name__ == '__main__':
    app.run()