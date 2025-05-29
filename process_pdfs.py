import os
import requests
from pathlib import Path

def process_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        response = requests.post('http://localhost:8000/process-pdf', files=files)
        print(f"Processing {pdf_path}: {response.json()}")

def main():
    stories_dir = Path('stories')
    for pdf_file in stories_dir.glob('*.pdf'):
        print(f"Processing {pdf_file}...")
        process_pdf(pdf_file)

if __name__ == "__main__":
    main() 