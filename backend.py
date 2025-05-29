from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv
import json
from openai import OpenAI
import random

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "story_chunks"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )

# Initialize database
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS story_chunks (
       id SERIAL PRIMARY KEY,
       book_title TEXT,
       chunk_text TEXT,
       chunk_index INTEGER
   )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()

def chunk_text(text, chunk_size=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1
        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    # Read PDF
    pdf_reader = PyPDF2.PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Chunk the text
    chunks = chunk_text(text)
    
    # Store in database
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get book title from filename
    book_title = os.path.splitext(file.filename)[0]
    
    # Prepare data for bulk insert
    data = [(book_title, chunk, i) for i, chunk in enumerate(chunks)]
    
    execute_values(
        cur,
        """
        INSERT INTO story_chunks (book_title, chunk_text, chunk_index)
        VALUES %s
        """,
        data
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"message": f"Processed {len(chunks)} chunks from {book_title}"}

def detect_language(text: str):
    system_prompt = "Detect the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de', 'it', 'pt') of the following text. Respond with only the code. If unsure, respond with 'en'."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0,
        max_tokens=2
    )
    return response.choices[0].message.content.strip().lower()

def generate_funny_response(query: str, context: str = None, language: str = "en"):
    system_prompt = f"""You are a witty and humorous storyteller who responds to questions about classic literature.\nIf the question is about the stories, provide a funny and engaging response based on the context.\nIf the question is unrelated to the stories, respond with a humorous 'I don't know' message.\nAlways maintain a playful and entertaining tone, using emojis and literary references.\nRespond in the user's language: {language}."""
    user_prompt = f"Question: {query}\n"
    if context:
        user_prompt += f"Context from story: {context}\n"
    user_prompt += "Please provide a funny and engaging response:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content

def generate_followup_question(query: str, context: str = None, language: str = "en"):
    followup_prompts = [
        "Ask a follow-up question related to the user's last question and the story context, or ask a random, fun question from the story universe.",
        "Come up with a playful or curious follow-up question about the story, or something whimsical from the world of classic tales.",
        "Suggest a question that would keep the conversation going, either based on the last answer or something fun from the story world."
    ]
    system_prompt = f"You are a witty and imaginative storyteller. After answering a user's question, you always suggest a follow-up question. Sometimes it's related to the last answer, sometimes it's a random, fun question from the world of classic stories. Respond in the user's language: {language}."
    user_prompt = f"User's question: {query}\n"
    if context:
        user_prompt += f"Story context: {context}\n"
    user_prompt += random.choice(followup_prompts)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.8,
        max_tokens=60
    )
    return response.choices[0].message.content.strip()

@app.get("/search")
async def search(query: str):
    language = detect_language(query)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT book_title, chunk_text
        FROM story_chunks
        WHERE chunk_text ILIKE %s
        LIMIT 5
    """, (f"%{query}%",))
    results = cur.fetchall()
    cur.close()
    conn.close()
    if results:
        result = random.choice(results)
        context = result[1]
        response = generate_funny_response(query, context, language)
        followup = generate_followup_question(query, context, language)
        return [{"book": result[0], "text": response, "followup": followup, "language": language}]
    else:
        response = generate_funny_response(query, language=language)
        followup = generate_followup_question(query, language=language)
        return [{"book": "Storyteller", "text": response, "followup": followup, "language": language}]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 