# Story Chat Interface

An interactive chat interface that uses AI to generate funny responses and images based on classic stories.

## Features

- Vector-based story search using FAISS
- Funny story responses using OpenAI
- Image generation using Fal AI
- Modern React frontend with Material-UI
- Flask backend with CORS support

## Prerequisites

- Python 3.8+
- Node.js 14+
- OpenAI API key
- Fal AI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd story-chat
```

2. Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=your_openai_key_here
FAL_AI_API_KEY=your_fal_ai_key_here
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
OPENAI_MODEL=gpt-3.5-turbo
SIMILARITY_THRESHOLD=0.7
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Set up the frontend:
```bash
cd frontend
npm install
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python app.py
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. Type your question about the stories in the chat input
2. The system will search for relevant story content
3. If found, you'll receive a funny response and an AI-generated image
4. If not found, you'll receive a humorous "I don't know" response

## Project Structure

```
story-chat/
├── .env                          # Environment variables
├── .gitignore
├── README.md
├── backend/
│   ├── app.py                   # Flask application
│   ├── requirements.txt
│   ├── story_processor.py       # PDF processing
│   ├── vector_store.py          # FAISS operations
│   └── data/
│       ├── pdfs/                # Story PDFs
│       ├── embeddings/          # FAISS index
│       └── processed/           # Processed chunks
└── frontend/
    ├── package.json
    └── src/
        └── App.js              # React application
```

## Adding New Stories

1. Place new PDF files in `backend/data/pdfs/`
2. Delete the `backend/data/embeddings/` directory
3. Restart the Flask application

## License

MIT 