import requests
import config

def chat_with_model(query, model=config.model_name, url=config.ollama_url):
    messages = [{"role": "user", "content": query}]
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json"
    }
    response = requests.post(url, json=payload)
    return response.json()['message']['content'].strip()