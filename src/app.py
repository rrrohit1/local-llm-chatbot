import gradio as gr
from utils import chat_with_model
import sqlite3
from datetime import datetime

# return user_input.lower() # Uncomment this line to see the user input echoed back
# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('chat_history.db')
c = conn.cursor()

# Create a table to store chat history if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                (timestamp TEXT, user_input TEXT, user_output TEXT)''')
conn.commit()

def save_to_db(user_input, user_output):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO chat_history (timestamp, user_input, user_output) VALUES (?, ?, ?)",
                (timestamp, user_input, user_output))
    conn.commit()
    conn.close()

def chat_response(user_input):
    user_output = chat_with_model(user_input)
    save_to_db(user_input, user_output)
    print_history()
    return user_output

def print_history():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()   
    c.execute("SELECT * FROM chat_history")
    rows = c.fetchall()
    for row in rows:
        print(row, flush=True)
    print(flush=True)
    conn.commit()
    conn.close()

with gr.Blocks() as demo:
    gr.Markdown("# Simple Chat App")
    chatbot = gr.Chatbot()
    user_input = gr.Textbox(label="Query")
    submit_btn = gr.Button("Send")
    
    def respond(chat_history, message):
        response = chat_response(message)
        chat_history.append((message, response))
        return chat_history, ""
    
    submit_btn.click(respond, [chatbot, user_input], [chatbot, user_input])

demo.launch()



