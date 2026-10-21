Agentic AI Customer Support System
About the Project
The Agentic AI Customer Support System is an AI-powered application designed to help customer support teams answer questions, search support documents, manage conversations, and track support tickets from one place.

The assistant uses information from a knowledge base to answer customer questions. If an issue needs human attention, the system can support ticket creation and escalation workflows.

This project is being developed step by step, starting with the backend and adding retrieval, agent workflows, and the user interface as each part is tested.

Features

- AI customer chat: A chat interface for customer questions.
- Knowledge base: Upload PDF, TXT, and Markdown support documents.
- Document processing: Extract text, split it into smaller chunks, and generate embeddings.
- Semantic search (RAG): Retrieve relevant document passages to help the AI answer questions using company information.
- Conversation history: Store and retrieve past conversations and messages.
- Ticket management: Create, view, and update support tickets.
- API backend: Expose functionality through FastAPI endpoints.
- Streamlit interface: Provide a simple dashboard for chat, tickets, conversations, knowledge documents, analytics, and settings.
- Agent workflow (planned): Use LangGraph to coordinate tools, memory, and human escalation.
Technology Stack
Technology	What we use it for
Python	Main programming language
FastAPI	Backend APIs
Streamlit	Web interface and dashboard
LangChain	Document splitting and LLM-related components
LangGraph	Agent workflow orchestration (planned integration)
OpenAI API	Language model responses and text embeddings
text-embedding-3-small	Converts text into vectors for semantic search
Qdrant	Stores and searches document vectors
PostgreSQL	Stores customers, conversations, messages, and support tickets
SQLAlchemy (async)	Database models and asynchronous database access
asyncpg	PostgreSQL async driver
PyMuPDF	Extracts text from PDF documents
pytest	Automated tests
Docker Compose	Runs local services such as PostgreSQL and Qdrant


How It Works

1. A support document is uploaded through the API.
2. The backend extracts text from the PDF, TXT, or Markdown file.
3. The text is split into smaller, overlapping chunks.
4. OpenAI generates an embedding for each chunk.
5. The chunks, vectors, and source metadata are saved in Qdrant.
6. When a customer asks a question, the system can search Qdrant for relevant passages.
7. The AI uses retrieved information to formulate a helpful response.
8. Conversations and support tickets are stored in PostgreSQL.
RAG stands for Retrieval-Augmented Generation. In simple terms, the system searches relevant company documents first, then uses that information to help generate an answer.
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/4d99f45c-08dd-4746-bfb5-2bd7b4977c09" />

