import json
import requests
import datetime
from cryptography.fernet import Fernet
from pymongo import MongoClient
import os
import csv
import openpyxl

class ultraChatBot():

    user_inputs = {}    
    
    conversation_state = 'welcome'  # Initial state
    current_field = None
    patient_data = None
    conversation_states = {} 

    def __init__(self, json):
        self.json = json
        if json is not None:
            self.dict_messages = json['data']
        else:
            self.dict_messages = None
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance85432/'
        self.token = 'b06msuy8lepgqr8c'
        

        
        # MongoDB connection
        # self.mongo_client = MongoClient('mongodb+srv://Cluster38639:bmBZcVFCTkx+@cluster38639.dbkdhck.mongodb.net')
        # self.db = self.mongo_client['patient_data']
        # self.collection = self.db['patient_records']

        # # Encryption key
        # self.encryption_key = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()

        # Initialize variables for conversational flow


    
    def handle_conversation(self, chatID, message):
        # print ('Before update', self.conversation_states)

        print(self.patient_data)

        user_input = message['body'].lower()

        if chatID not in self.conversation_states:
            self.conversation_states[chatID] = 'welcome'  # Set initial conversation state for new chat

        conversation_state = self.conversation_states[chatID]

        if self.patient_data is None:
            self.patient_data = {
                'full_name': '',
                'date_of_birth': '',
                'gender': '',
                'address': '',
                'medical_history': '',
                'current_medications': ''
            }

        if conversation_state == 'welcome':
            return self.welcome(chatID)

        elif conversation_state == 'collect_full_name':
            self.patient_data['full_name'] = user_input
            self.send_message(chatID, "Please provide your date of birth (DD/MM/YYYY).")
            self.conversation_states[chatID]= 'collect_date_of_birth'
            self.current_field = 'date_of_birth'
            return self.send_message(chatID, "Please provide your date of birth (DD/MM/YYYY).")


        elif conversation_state == 'collect_date_of_birth':
            self.patient_data['date_of_birth'] = user_input
            self.send_message(chatID, "Please specify your gender (Male/Female/Other).")
            self.conversation_states[chatID]= 'collect_gender'
            self.current_field = 'gender'
            return self.send_message(chatID, "Please specify your gender (Male/Female/Other).")

        elif conversation_state == 'collect_gender':
            self.patient_data['gender'] = user_input
            self.send_message(chatID, "Please provide your address")
            self.conversation_states[chatID]= 'collect_address'
            self.current_field = 'address'
            return self.send_message(chatID, "Please provide your address.")

        elif conversation_state == 'collect_address':
            self.patient_data['address'] = user_input
            self.send_message(chatID, "Please provide your medical history")
            self.conversation_states[chatID]= 'collect_medical_history'
            self.current_field = 'medical_history'
            return self.send_message(chatID, "Please provide your medical history.")

        elif conversation_state == 'collect_medical_history':
            self.patient_data['medical_history'] = user_input
            self.send_message(chatID, "Please provide your current medications(if any)")
            self.conversation_states[chatID]= 'collect_current_medications'
            self.current_field = 'current_medications'
            return self.send_message(chatID, "Please provide your current medications (if any).")

        elif conversation_state == 'collect_current_medications':
            self.patient_data['current_medications'] = user_input
            self.send_message(chatID, "Thank you for providing your information. Your data has been securely stored.")
            # self.store_data_securely()  # Call the method to store data securely
            self.send_message(chatID, "Please choose an export option: \n1. CSV\n2. Excel")
            self.conversation_states[chatID]= 'export_data'
            return self.send_message(chatID, "Please choose an export option: \n1. CSV\n2. Excel")
        elif conversation_state == 'export_data':
            if user_input == '1':
                self.export_to_csv()
                # self.send_message(chatID, "Your data has been exported to a CSV file.")
                return self.send_message(chatID, "Your data has been exported to a CSV file.")
            elif user_input == '2':
                self.export_to_excel()
                # self.send_message(chatID, "Your data has been exported to an Excel file.")
                return self.send_message(chatID, "Your data has been exported to an Excel file.")
            else:
                return self.send_message(chatID, "Invalid option. Please choose 1, or 2.")

        else:
            return self.send_message(chatID, "I'm sorry, I didn't understand your response. Please try again.")
        
        

   
    # def store_data_securely(self):
    #     # Encrypt the patient data
    #     fernet = Fernet(self.encryption_key)
    #     encrypted_data = fernet.encrypt(str(self.patient_data).encode())

    #     # Store the encrypted data in MongoDB
    #     record = {
    #         'encrypted_data': encrypted_data
    #     }
    #     self.collection.insert_one(record)
    #     print("Patient data stored securely in MongoDB.")
    

    def export_to_csv(self):
    # Write the patient data to a CSV file
        with open('patient_data.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.patient_data.keys())
            writer.writeheader()
            writer.writerow(self.patient_data)
    


    def export_to_excel(self):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        
        headers = list(self.patient_data.keys())
        worksheet.append(headers)
        
        data_row = list(self.patient_data.values())
        worksheet.append(data_row)
        workbook.save('patient_data.xlsx')
        print("Patient data exported to 'patient_data.xlsx'")


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


    def welcome(self, chatID = None):
        print(chatID)
        welcome_message = "Hi! Welcome to the WhatsApp Patient Data Collection Bot. I will ask you a series of questions to collect your personal and medical information. Please provide accurate responses. Let's start with your full name."
        self.send_message(chatID, welcome_message)
        self.conversation_state = 'collect_full_name'
        self.current_field = 'full_name'
        self.conversation_states[chatID]= 'collect_full_name'
        print(self.conversation_states)
        return self.send_message(chatID, welcome_message)


    # def Processingـincomingـmessages(self):
    #     if self.dict_messages != []:
    #         message =self.dict_messages
    #         text = message['body'].split()
    #         if not message['fromMe']:
    #             chatID  = message['from'] 
    #             if text[0].lower() == 'hi':
    #                 return self.welcome(chatID)
    #             elif text[0].lower() == 'time':
    #                 return self.time(chatID)
    #             elif text[0].lower() == 'image':
    #                 return self.send_image(chatID)
    #             elif text[0].lower() == 'video':
    #                 return self.send_video(chatID)
    #             elif text[0].lower() == 'audio':
    #                 return self.send_audio(chatID)
    #             elif text[0].lower() == 'voice':
    #                 return self.send_voice(chatID)
    #             elif text[0].lower() == 'contact':
    #                 return self.send_contact(chatID)
    #             else:
    #                 return self.welcome(chatID, True)
    #         else: return 'NoCommand'

    def ProcessingIncomingMessages(self):
        print("ProcessingIncomingMessages method is called")
        print("Received messages:", self.dict_messages)
        
        if self.dict_messages is None:
            print("No messages received. Invoking welcome method...")
            return self.welcome()  # Assuming chatID needs to be passed here, adjust as necessary
        
        # Check if the received messages is a list and not empty
        if self.dict_messages:
            # Extract the first message
            message = self.dict_messages
            
            # Extract message body and sender's ID
            message_body = message['body'].lower()
            sender_id = message['from']
            
            # Check if the message is not sent by the bot
            if not message['fromMe']:
                # Process the message
                response = self.handle_conversation(sender_id, message)
                print(response)
                
                if response:
                    print("Returning response:", response)
                    return response
            else:
                print("NoCommand")
                return 'NoCommand'
        else:
            print("Invalid message format or no messages received.")
            return 'No message received'
