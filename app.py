import streamlit as st
import requests
import random
import os
from deepgram import Deepgram
import openai
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Supported OpenAI TTS voices and their languages
OPENAI_TTS_LANGUAGES = {
    'en': 'onyx',      # English
    'es': 'nova',     # Spanish
    'fr': 'fable',    # French
    'de': 'alloy',    # German
    'it': 'echo',     # Italian
    'pt': 'shimmer',  # Portuguese
}

def transcribe_audio(audio_bytes):
    dg_client = Deepgram(DEEPGRAM_API_KEY)
    response = dg_client.transcription.prerecorded(
        {"buffer": audio_bytes, "mimetype": "audio/wav"},
        {"punctuate": True, "language": "en"}
    )
    return response['results']['channels'][0]['alternatives'][0]['transcript']

def get_story_response(query):
    try:
        response = requests.get(f"http://localhost:8000/search?query={query}")
        if response.status_code == 200:
            results = response.json()
            if results:
                result = results[0]
                return f"📚 From {result['book']}:\n\n{result['text']}"
            else:
                return "Oops! My storybook is having a technical hiccup! 📚"
        else:
            return "Oops! My storybook is having a technical hiccup! 📚"
    except:
        return "My magic carpet seems to be out of service! 🧞‍♂️"

def tts_openai(text, language_code='en'):
    voice = OPENAI_TTS_LANGUAGES.get(language_code, 'onyx')
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    return BytesIO(response.content)

def generate_image(prompt):
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response.data[0].url

# Set page config
st.set_page_config(
    page_title="Story Time Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #4a5568;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .book-badges {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .book-badge {
        background: linear-gradient(135deg, #ff6b6b, #ffa500);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(255, 107, 107, 0.3);
    }
    
    /* Chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        position: relative;
        animation: fadeInUp 0.3s ease-out;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin-left: 2rem;
        align-self: flex-end;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, #f7fafc, #edf2f7);
        color: #2d3748;
        margin-right: 2rem;
        align-self: flex-start;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(102, 126, 234, 0.2);
        border-radius: 15px;
        padding: 0.8rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* Voice input section */
    .voice-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .voice-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.8);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
        background: rgba(255, 255, 255, 0.9);
    }
    
    /* Audio player styling */
    .stAudio {
        margin: 0.5rem 0;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .chat-message.user {
            margin-left: 1rem;
        }
        
        .chat-message.assistant {
            margin-right: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Header section
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">📚 Story Time Chat</h1>
        <p class="subtitle">
            Discover magical stories and adventures! Ask me anything about your favorite classic tales.
            <br>You can type, record, or upload your question as audio.
        </p>
        <div class="book-badges">
            <span class="book-badge">🐰 Alice in Wonderland</span>
            <span class="book-badge">⚓ Gulliver's Travels</span>
            <span class="book-badge">🧞‍♂️ Arabian Nights</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add a session state for followup
if "followup" not in st.session_state:
    st.session_state.followup = None

# Helper to get response, followup, and audio
def get_full_response(query):
    response_data = requests.get(f"http://localhost:8000/search?query={query}").json()
    print("DEBUG: Backend response:", response_data)  # Debug print
    if response_data:
        result = response_data[0]
        response = f"📚 From {result['book']}:\n\n{result['text']}"
        followup = result.get("followup", None)
        language = result.get("language", "en")
        audio_response = tts_openai(response, language)
        return response, followup, audio_response
    return "Oops! My storybook is having a technical hiccup! 📚", None, None

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    st.markdown(f"""
        <div class="chat-message {message['role']}">
            {message['content'].replace(chr(10), '<br>')}
        </div>
    """, unsafe_allow_html=True)
    
    if message["role"] == "assistant" and "audio" in message:
        st.audio(message["audio"], format="audio/mp3")
    
    # Show followup if present
    if message["role"] == "assistant" and "followup" in message and message["followup"]:
        if st.button(f"💡 {message['followup']}", key=f"followup_{idx}"):
            st.session_state.messages.append({"role": "user", "content": message["followup"]})
            response, followup, audio_response = get_full_response(message["followup"])
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response, "followup": followup})
            st.rerun()
    
    # Image generation button and display
    if message["role"] == "assistant":
        if st.button("🖼️ Generate Image", key=f"img_{idx}"):
            with st.spinner("Creating magical artwork..."):
                image_url = generate_image(message["content"])
                st.image(image_url, caption="Generated by DALL·E", use_column_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Voice input section
st.markdown("""
    <div class="voice-section">
        <div class="voice-title">🎤 Voice Input</div>
    </div>
""", unsafe_allow_html=True)

audio_file = st.file_uploader("Upload or record your question", type=["wav", "mp3"], help="Supported formats: WAV, MP3")

if audio_file is not None:
    audio_bytes = audio_file.read()
    with st.spinner("🎧 Transcribing your voice..."):
        try:
            transcript = transcribe_audio(audio_bytes)
            st.success(f"✨ You said: **{transcript}**")
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": transcript})
            # Get response, followup, and audio
            response, followup, audio_response = get_full_response(transcript)
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response, "followup": followup})
            st.rerun()
        except Exception as e:
            st.error(f"❌ Transcription failed: {e}")

# Text chat input
if prompt := st.chat_input("What would you like to know? ✨"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Get response, followup, and audio
    with st.spinner("📖 Searching through the storybooks..."):
        response, followup, audio_response = get_full_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response, "followup": followup})
    st.rerun()