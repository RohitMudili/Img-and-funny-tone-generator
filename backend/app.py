import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai
import requests
from story_processor import StoryProcessor
from vector_store import VectorStore
from image_generator import ImageGenerator

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
CORS(app)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize story processor and vector store
pdf_dir = os.path.join(os.path.dirname(__file__), 'data', 'pdfs')
embeddings_dir = os.path.join(os.path.dirname(__file__), 'data', 'embeddings')
processed_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')

story_processor = StoryProcessor(pdf_dir, embeddings_dir, processed_dir)
vector_store = VectorStore()
image_generator = ImageGenerator(
    fal_ai_key=os.getenv('FAL_AI_API_KEY'),
    openai_key=os.getenv('OPENAI_API_KEY')
)

# Process PDFs and load index
chunks, index = story_processor.load_or_process_pdfs()
vector_store.load_index(os.path.join(embeddings_dir, 'faiss_index.bin'), chunks)

def generate_funny_response(story_chunks: list) -> str:
    """Generate a funny response using OpenAI."""
    prompt = f"""Based on these story excerpts:
    {chr(10).join(story_chunks)}
    
    Tell me a funny and engaging story that incorporates these elements. 
    Make it humorous and entertaining while staying true to the original content."""
    
    response = openai.ChatCompletion.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        messages=[
            {"role": "system", "content": "You are a witty and humorous storyteller."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('message', '')
    
    # Check if query is relevant to stories
    if not vector_store.is_query_relevant(query):
        # Generate confused image for unrelated queries
        image_url = image_generator.generate_confused_image()
        return jsonify({
            "message": "Well, that's about as related to my stories as a fish is to bicycle repair! I only know about the stories I've read.",
            "image_url": image_url,
            "relevant": False
        })
    
    # Get relevant story chunks
    story_chunks, scores = vector_store.search(query)
    
    # Generate funny response
    response_text = generate_funny_response(story_chunks)
    
    # Generate image based on the response
    image_url = image_generator.generate_story_image(response_text)
    
    return jsonify({
        "message": response_text,
        "image_url": image_url,
        "relevant": True
    })

if __name__ == '__main__':
    app.run(debug=True) 