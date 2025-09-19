from transformers import pipeline
from os import listdir, path
from docx import Document
from PyPDF2 import PdfReader
import textwrap


import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
summarizer = None
           

def read_file(file_path: str) -> str | None:
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            if text.strip():
                return text.strip()
            
            return None
        
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ''
            
            for page in reader.pages:
                extracted = page.extract_text()
                
                if extracted:
                    text += extracted + '\n'

            if text.strip():
                return text.strip()
            
            return None

    if file_path.endswith('.docx'):
        doc = Document(file_path)
        text = []
        
        for para in doc.paragraphs:
            text.append(para.text)

        if text:
            return '\n'.join(text).strip()
        
        return None

    return None


def generate_summary(text: str) -> str:
    global summarizer
    if summarizer is None:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        
    if len(text.split()) < 1000:
        summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        return summary.strip().replace(' .', '.')

    chunks = textwrap.wrap(text, width=2000)
    partial_summaries = []

    for chunk in chunks[:3]:
        summary = summarizer(chunk, max_length=80, min_length=60, do_sample=False)[0]['summary_text']
        partial_summaries.append(summary)

    merged = " ".join(partial_summaries)
    final_summary = summarizer(merged, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    return final_summary.strip().replace(' .', '.')


if __name__ == "__main__":
    fpath: str = path.join(path.dirname(__file__), 'test_samples')
    filenames: list[str] = listdir(fpath)
    filenames = [f for f in filenames if path.isfile(path.join(fpath, f))]

    file: str = filenames[0]  
    file_path: str = path.join(fpath, file)
        
    text: str | None = read_file(file_path)
    if text:
        summary: str | None = generate_summary(text)
        if summary:
            print(f"\nSummary for {file}:\n{summary}")
            