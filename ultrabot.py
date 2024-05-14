import json
import requests
import datetime

class ultraChatBot():    
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['data']
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance85432/'
        self.token = 'b06msuy8lepgqr8c'
        
        # Initialize patient data dictionary
        self.patient_data = {
            'full_name': '',
            'date_of_birth': '',
            'gender': '',
            'address': '',
            'medical_history': '',
            'current_medications': ''
        }
        
        # Initialize variables for conversational flow
        self.conversation_state = 'welcome'  # Initial state
        self.current_field = None

   
    def send_requests(self, type, data):
        url = f"{self.ultraAPIUrl}{type}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatID, text):
        data = {"to" : chatID,
                "body" : text}  
        answer = self.send_requests('messages/chat', data)
        return answer

    def send_image(self, chatID):
        data = {"to" : chatID,
                "image" : "https://file-example.s3-accelerate.amazonaws.com/images/test.jpeg"}  
        answer = self.send_requests('messages/image', data)
        return answer

    def send_video(self, chatID):
        data = {"to" : chatID,
                "video" : "https://file-example.s3-accelerate.amazonaws.com/video/test.mp4"}  
        answer = self.send_requests('messages/video', data)
        return answer

    def send_audio(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/audio/2.mp3"}  
        answer = self.send_requests('messages/audio', data)
        return answer


    def send_voice(self, chatID):
        data = {"to" : chatID,
                "audio" : "https://file-example.s3-accelerate.amazonaws.com/voice/oog_example.ogg"}  
        answer = self.send_requests('messages/voice', data)
        return answer

    def send_contact(self, chatID):
        data = {"to" : chatID,
                "contact" : "14000000001@c.us"}  
        answer = self.send_requests('messages/contact', data)
        return answer


    def time(self, chatID):
        t = datetime.datetime.now()
        time = t.strftime('%Y-%m-%d %H:%M:%S')
        return self.send_message(chatID, time)


    def welcome(self, chatID):
        welcome_message = "Hi! Welcome to the WhatsApp Patient Data Collection Bot. I will ask you a series of questions to collect your personal and medical information. Please provide accurate responses. Let's start with your full name."
        self.send_message(chatID, welcome_message)
        self.conversation_state = 'collect_full_name'
        self.current_field = 'full_name'
        # return self.send_message(chatID, welcome_string)


    def Processingـincomingـmessages(self):
        if self.dict_messages != []:
            message =self.dict_messages
            text = message['body'].split()
            if not message['fromMe']:
                chatID  = message['from'] 
                if text[0].lower() == 'hi':
                    return self.welcome(chatID)
                elif text[0].lower() == 'time':
                    return self.time(chatID)
                elif text[0].lower() == 'image':
                    return self.send_image(chatID)
                elif text[0].lower() == 'video':
                    return self.send_video(chatID)
                elif text[0].lower() == 'audio':
                    return self.send_audio(chatID)
                elif text[0].lower() == 'voice':
                    return self.send_voice(chatID)
                elif text[0].lower() == 'contact':
                    return self.send_contact(chatID)
                else:
                    return self.welcome(chatID, True)
            else: return 'NoCommand'