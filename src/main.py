from typing import Optional, List
import sqlite3
from pathlib import Path
import PyPDF2
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class DocumentProcessor:
    def process_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF documents"""
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

class Database:
    def __init__(self, db_path: str = "chat_history.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_input TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                content TEXT,
                filename TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def save_message(self, user_input: str, bot_response: str):
        self.conn.execute(
            "INSERT INTO messages (user_input, bot_response) VALUES (?, ?)",
            (user_input, bot_response)
        )
        self.conn.commit()

    def save_document(self, content: str, filename: str):
        self.conn.execute(
            "INSERT INTO documents (content, filename) VALUES (?, ?)",
            (content, filename)
        )
        self.conn.commit()

class LocalLLM:
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,  # Use float32 for CPU
            device_map="cpu"
        )
    
    def generate_response(self, prompt: str, max_length: int = 100) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

class ChatApp:
    def __init__(self):
        self.db = Database()
        self.doc_processor = DocumentProcessor()
        self.llm = LocalLLM()
        
    def process_document(self, file_path: str):
        content = self.doc_processor.process_pdf(file_path)
        self.db.save_document(content, Path(file_path).name)
        return "Document processed and stored successfully"
    
    def chat(self, user_input: str) -> str:
        # Generate response using the local LLM
        response = self.llm.generate_response(user_input)
        
        # Save the conversation to database
        self.db.save_message(user_input, response)
        
        return response

def main():
    app = ChatApp()
    
    # Example usage
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
            
        if user_input.startswith("process_pdf:"):
            pdf_path = user_input.split(":", 1)[1].strip()
            print(app.process_document(pdf_path))
        else:
            response = app.chat(user_input)
            print(f"Bot: {response}")

if __name__ == "__main__":
    main()
