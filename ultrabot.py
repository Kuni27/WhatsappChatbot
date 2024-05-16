import json
import requests
from cryptography.fernet import Fernet
from pymongo import MongoClient
import sqlite3
import os
import csv
import openpyxl
import datetime

class ultraChatBot():

    user_inputs = {}    
    
    conversation_state = 'welcome'  # Initial state
    current_field = None
    patient_data = None
    conversation_states = {} 
    user_inputs = {}

    def __init__(self, json):
        self.json = json
        if json is not None:
            self.dict_messages = json['data']
        else:
            self.dict_messages = None
        
        # credentials for the WhatsApp API, needs to be configured
        self.ultraAPIUrl = 'https://api.ultramsg.com/instance85432/'
        self.token = 'b06msuy8lepgqr8c'

        # SQLite connection
        self.conn = sqlite3.connect('patient_data.db')
        self.create_table()

        # Encryption key
        self.encryption_key = os.environ.get('ENCRYPTION_KEY') or Fernet.generate_key()

    #create the tables if it is not present in the database.
    def create_table(self):
            c = self.conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS patient_records (
                            chatID TEXT PRIMARY KEY,
                            encrypted_data TEXT
                        )''')
            self.conn.commit()
    
    # This is our main method that handles the whole code flow. It initially sets the conversation state to welcome for a new user and then keeps a track of the 
    # conversaton state for the whole time. It also saves the information that we got from the chat bot and stores in in a data base. We can also download the data 
    # from the database either in .csv format or .xlsx format as per the user input.
    def handle_conversation(self, chatID, message):
        user_input = message['body']

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

        if chatID not in self.user_inputs:
            self.user_inputs[chatID] = {}

        # print('The data stored',self.user_inputs )

        if conversation_state == 'welcome':
            return self.welcome(chatID)

        elif conversation_state == 'collect_full_name':
            self.user_inputs[chatID]['full_name'] = user_input
            self.conversation_states[chatID]= 'collect_date_of_birth'
            self.current_field = 'date_of_birth'
            return self.send_message(chatID, "Please provide your date of birth (DD/MM/YYYY).")
    
        elif conversation_state == 'collect_date_of_birth':
            try:
                dob = datetime.datetime.strptime(user_input, '%d/%m/%Y')
            except ValueError:
               return self.send_message(chatID, "Invalid date format. Please provide your date of birth in the format DD/MM/YYYY.") 
            self.user_inputs[chatID]['date_of_birth'] = user_input
            self.conversation_states[chatID]= 'collect_gender'
            self.current_field = 'gender'
            return self.send_message(chatID, "Please specify your gender (Male/Female/Other).")
        

        elif conversation_state == 'collect_gender':
            if user_input.lower() not in ['male', 'female', 'other']:
                return self.send_message(chatID, "Invalid input. Please specify your gender as Male, Female, or Other.")
            else:
                self.user_inputs[chatID]['gender'] = user_input
                self.conversation_states[chatID]= 'collect_address'
                self.current_field = 'address'
                return self.send_message(chatID, "Please provide your address.")

        elif conversation_state == 'collect_address':
            self.user_inputs[chatID]['address'] = user_input
            self.conversation_states[chatID]= 'collect_medical_history'
            self.current_field = 'medical_history'
            return self.send_message(chatID, "Please provide your medical history including but not limited to allergies, previous surgeries . Please type NA is there isn't any")

        elif conversation_state == 'collect_medical_history':
            self.user_inputs[chatID]['medical_history'] = user_input
            self.conversation_states[chatID]= 'collect_current_medications'
            self.current_field = 'current_medications'
            return self.send_message(chatID, "Please provide your current medications. Please type in NA if there isn't any")

        elif conversation_state == 'collect_current_medications':
            self.user_inputs[chatID]['current_medications'] = user_input
            self.send_message(chatID, "Thank you for providing your information. Your data has been securely stored.")
            self.conversation_states[chatID]= 'export_data'
            return self.send_message(chatID, "Please choose an export option: \n1. CSV\n2. Excel")
        
        elif conversation_state == 'export_data':
            self.store_data_securely(chatID)
            if user_input == '1':
                self.export_to_csv()
                response_message = "Your data has been exported to a CSV file."
            elif user_input == '2':
                self.export_to_excel()
                response_message = "Your data has been exported to an Excel file."
            else:
                return self.send_message(chatID, "Invalid option. Please choose 1, or 2.")
            
            # Reset conversation states and user inputs
            self.conversation_states[chatID] = 'welcome'
            self.user_inputs = {}
            return self.send_message(chatID, response_message)

        else:
            return self.send_message(chatID, "I'm sorry, I didn't understand your response. Please try again.")

    # This method encrypts the data before storing it into the data base. This helps in maintaining the data security for the users.  
    def store_data_securely(self, chatID):
        # Encrypt the patient data
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(str(self.user_inputs[chatID]).encode())
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO patient_records (chatID, encrypted_data) VALUES (?, ?)", (chatID, encrypted_data.decode()))
        self.conn.commit()
        print("Patient data stored securely in SQLite.")
    
    #This method downloads the data in the .csv format.
    def export_to_csv(self):
        # Write the patient data to a CSV file
        with open('patient_data.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.user_inputs[next(iter(self.user_inputs))].keys())
            writer.writeheader()
            for user_id, data in self.user_inputs.items():
                writer.writerow(data)

    #This method downloads the data in the .xlsx format.
    def export_to_excel(self):
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        
        # Get the headers from the first user's data
        headers = list(self.user_inputs[next(iter(self.user_inputs))].keys())
        worksheet.append(headers)
        
        # Write each user's data to the worksheet
        for data in self.user_inputs.values():
            data_row = list(data.values())
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

    # This method addresses the initial state of the coversation which is 'Welcome' and changes the state for the further iterations.
    def welcome(self, chatID = None):
        print(chatID)
        welcome_message = "Hi! Welcome to the WhatsApp Patient Data Collection Bot. I will ask you a series of questions to collect your personal and medical information. Please provide accurate responses. Let's start with your full name."
        self.conversation_state = 'collect_full_name'
        self.current_field = 'full_name'
        self.conversation_states[chatID]= 'collect_full_name'
        return self.send_message(chatID, welcome_message)

    # This is the starting point of our work flow. When a conversation is initiated from the WhatsApp API, this method is triggered. And it fetched the chatID 
    # and message from the payload that we get the the api repsonse and uses it for the further processing.

    # A sample payload looks like this:

    # {'id': 'false_919954963162@c.us_3EB0CB7828A3C938E48A07', 'from': '919954963162@c.us', 'to': '19793444259@c.us', 'author': '', 'pushname': 'Manisha Panda', 
    #'ack': '', 'type': 'chat', 'body': 'College Station, Texas. 77840', 'media': '', 'fromMe': False, 'self': False, 'isForwarded': False, 'isMentioned': False, 
    # 'quotedMsg': {}, 'mentionedIds': [], 'time': 1715788978} 

    def ProcessingIncomingMessages(self):
        print("ProcessingIncomingMessages method is called")
        print("Received messages:", self.dict_messages)
        
        if self.dict_messages is None:
            print("No messages received. Invoking welcome method...")
            return self.welcome()
        
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
