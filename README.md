# Story Time Chat

A fun chat interface that lets you ask questions about classic stories and get responses in a humorous tone!

## Features

- PDF processing and chunking
- PostgreSQL database for story storage
- FastAPI backend
- Streamlit chat interface with a funny tone
- OpenAI-powered humorous responses
- Support for multiple classic books

## Setup

1. Install PostgreSQL and create a database named `story_chunks`

2. Create a `.env` file with your database credentials and OpenAI API key:
```
DB_NAME=story_chunks
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Start the backend server:
```bash
python backend.py
```

5. Process the PDFs:
```bash
python process_pdfs.py
```

6. Start the Streamlit interface:
```bash
streamlit run app.py
```

## Usage

1. Open your browser and go to `http://localhost:8501`
2. Type your question in the chat input
3. Get responses from the stories in a funny tone!

## Supported Books

- Alice in Wonderland
- Gulliver's Travels
- The Arabian Nights

## Note

Make sure to have:
- PostgreSQL running and the database created before starting the application
- A valid OpenAI API key in your `.env` file 