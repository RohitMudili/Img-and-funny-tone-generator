import os
import json
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Tuple

class StoryProcessor:
    def __init__(self, pdf_dir: str, embeddings_dir: str, processed_dir: str):
        self.pdf_dir = pdf_dir
        self.embeddings_dir = embeddings_dir
        self.processed_dir = processed_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 3  # Number of sentences per chunk
        
        # Create directories if they don't exist
        os.makedirs(embeddings_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks of sentences."""
        sentences = text.replace('\n', ' ').split('.')
        chunks = []
        current_chunk = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                current_chunk.append(sentence)
                if len(current_chunk) >= self.chunk_size:
                    chunks.append('. '.join(current_chunk) + '.')
                    current_chunk = []
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def process_pdfs(self) -> Tuple[List[str], np.ndarray]:
        """Process all PDFs in the directory and create embeddings."""
        all_chunks = []
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_dir, pdf_file)
            text = self.extract_text_from_pdf(pdf_path)
            chunks = self.split_into_chunks(text)
            all_chunks.extend(chunks)
        
        # Generate embeddings
        embeddings = self.model.encode(all_chunks)
        
        # Save chunks and embeddings
        self._save_processed_data(all_chunks, embeddings)
        
        return all_chunks, embeddings
    
    def _save_processed_data(self, chunks: List[str], embeddings: np.ndarray):
        """Save processed chunks and embeddings."""
        # Save chunks
        chunks_file = os.path.join(self.processed_dir, 'story_chunks.json')
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        # Save FAISS index
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings.astype('float32'))
        faiss.write_index(index, os.path.join(self.embeddings_dir, 'faiss_index.bin'))
    
    def load_or_process_pdfs(self) -> Tuple[List[str], np.ndarray]:
        """Load existing processed data or process PDFs if needed."""
        chunks_file = os.path.join(self.processed_dir, 'story_chunks.json')
        index_file = os.path.join(self.embeddings_dir, 'faiss_index.bin')
        
        if os.path.exists(chunks_file) and os.path.exists(index_file):
            # Load existing data
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            index = faiss.read_index(index_file)
            return chunks, index
        
        # Process PDFs if data doesn't exist
        return self.process_pdfs() 