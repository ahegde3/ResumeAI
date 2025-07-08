import mimetypes
import PyPDF2
import docx
import csv
from pathlib import Path
import os

def _read_simple_file_content(file_path: str) -> str:
    with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
            return content
    
def _read_pdf_file_content(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        return "\n\n".join([page.extract_text() for page in pdf_reader.pages])

def _read_docx_file_content(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def _read_csv_file_content(file_path: str) -> str:
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        return "\n".join([",".join(row) for row in csv_reader])



def extract_file_content(file_path: str, max_length: int = 10000) -> str:
    """
    Extract content from a file based on its type.
    
    Args:
        file_path: Path to the file
        max_length: Maximum length of content to extract
        
    Returns:
        String containing the extracted content
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Text files (including .tex)
    if mime_type in ['text/plain', 'text/markdown', 'application/json', 'text/html', 'text/css', 'text/javascript'] or file_path.suffix in ['.txt', '.md', '.json', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.ts', '.tsx', '.jsx', '.tex']:
        return _read_simple_file_content(file_path)[:max_length]
    
    # PDF files
    elif mime_type == 'application/pdf' or file_path.suffix == '.pdf':
        try:
            return _read_pdf_file_content(file_path)[:max_length]
        except Exception as e:
            return f"Error extracting PDF content: {str(e)}"
    
    # Word documents
    elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] or file_path.suffix in ['.doc', '.docx']:
        try:
            return _read_docx_file_content(file_path)[:max_length]
        except Exception as e:
            return f"Error extracting Word document content: {str(e)}"
    
    # CSV files
    elif mime_type == 'text/csv' or file_path.suffix == '.csv':
        try:
            return _read_csv_file_content(file_path)[:max_length]
        except Exception as e:
            return f"Error extracting CSV content: {str(e)}"
    
    # Images and other binary files
    else:
        return f"[File content not extracted: {file_path.name} is a {mime_type or 'binary'} file]"

def get_latest_uploaded_file_content(upload_dir="app/uploads"):
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    if not files:
        return None
    return extract_file_content(os.path.join(upload_dir, files[-1]))