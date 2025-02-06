# local-llm-chatbot
Building a chatbot hosted locally on a CPU.

# Workflow
## Local LLM Integration

- Uses TinyLlama (1.1B parameters), which can run on CPU with 8GB RAM
- Configurable for other small models like GPT2-small or BERT
- Runs inference in float32 for CPU compatibility
  
## Document Processing

- PDF text extraction using PyPDF2
- Stores document content in SQLite database
- Extensible for other document types


## Database Management

- SQLite for storing chat history and documents
- Separate tables for messages and documents
- Timestamps for all entries

## Main Application

- Simple command-line interface
- Handles both chat and document processing
- Modular design for easy extension
