import gradio as gr
from utils import chat_with_model

def chat_response(user_input):
    # return user_input.lower() # Uncomment this line to see the user input echoed back
    return chat_with_model(user_input)

with gr.Blocks() as demo:
    gr.Markdown("# Simple Chat App")
    chatbot = gr.Chatbot()
    user_input = gr.Textbox(label="Your Message")
    submit_btn = gr.Button("Send")
    
    def respond(chat_history, message):
        response = chat_response(message)
        chat_history.append((message, response))
        return chat_history, ""
    
    submit_btn.click(respond, [chatbot, user_input], [chatbot, user_input])

demo.launch()
