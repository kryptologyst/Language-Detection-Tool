from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime
import os
from langdetect import detect, detect_langs, LangDetectException
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Language Detection Tool",
    description="A modern language detection service with web interface",
    version="2.0.0"
)

# Database setup
DB_PATH = "language_detection.db"

def init_database():
    """Initialize SQLite database with tables for language samples and detection history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create language samples table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS language_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            language_code TEXT NOT NULL,
            language_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create detection history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT NOT NULL,
            detected_language TEXT NOT NULL,
            confidence REAL NOT NULL,
            all_languages TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if not exists
    cursor.execute('SELECT COUNT(*) FROM language_samples')
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Hello, how are you today?", "en", "English"),
            ("Bonjour, comment allez-vous?", "fr", "French"),
            ("Hola, ¿cómo estás?", "es", "Spanish"),
            ("Hallo, wie geht es dir?", "de", "German"),
            ("Ciao, come stai?", "it", "Italian"),
            ("Olá, como você está?", "pt", "Portuguese"),
            ("Привет, как дела?", "ru", "Russian"),
            ("こんにちは、元気ですか？", "ja", "Japanese"),
            ("안녕하세요, 어떻게 지내세요?", "ko", "Korean"),
            ("你好，你好吗？", "zh-cn", "Chinese"),
            ("مرحبا، كيف حالك؟", "ar", "Arabic"),
            ("नमस्ते, आप कैसे हैं?", "hi", "Hindi"),
            ("Hej, hur mår du?", "sv", "Swedish"),
            ("Hei, hvordan har du det?", "no", "Norwegian"),
            ("Hej, hvordan har du det?", "da", "Danish"),
            ("Hoi, hoe gaat het?", "nl", "Dutch"),
            ("Cześć, jak się masz?", "pl", "Polish"),
            ("Привіт, як справи?", "uk", "Ukrainian"),
            ("Merhaba, nasılsın?", "tr", "Turkish"),
            ("Γεια σας, πώς είστε;", "el", "Greek")
        ]
        
        cursor.executemany(
            'INSERT INTO language_samples (text, language_code, language_name) VALUES (?, ?, ?)',
            sample_data
        )
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

# Templates setup
templates = Jinja2Templates(directory="templates")

# Pydantic models
class DetectionRequest(BaseModel):
    text: str
    threshold: Optional[float] = 0.5

class DetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    all_languages: List[Dict[str, Any]]
    success: bool
    message: Optional[str] = None

class BatchDetectionRequest(BaseModel):
    texts: List[str]
    threshold: Optional[float] = 0.5

class LanguageStats(BaseModel):
    total_detections: int
    most_common_language: str
    average_confidence: float
    languages_detected: Dict[str, int]

# Language code to name mapping
LANGUAGE_NAMES = {
    'en': 'English', 'fr': 'French', 'es': 'Spanish', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
    'ko': 'Korean', 'zh-cn': 'Chinese', 'zh-tw': 'Traditional Chinese',
    'ar': 'Arabic', 'hi': 'Hindi', 'sv': 'Swedish', 'no': 'Norwegian',
    'da': 'Danish', 'nl': 'Dutch', 'pl': 'Polish', 'uk': 'Ukrainian',
    'tr': 'Turkish', 'el': 'Greek', 'he': 'Hebrew', 'th': 'Thai',
    'vi': 'Vietnamese', 'id': 'Indonesian', 'ms': 'Malay', 'tl': 'Filipino'
}

def detect_language_with_confidence(text: str, threshold: float = 0.5) -> Dict[str, Any]:
    """Detect language with confidence and error handling"""
    try:
        if not text.strip():
            raise ValueError("Empty text provided")
        
        detected_lang = detect(text)
        all_languages = detect_langs(text)
        
        # Convert to list of dictionaries
        languages_list = []
        for lang in all_languages:
            languages_list.append({
                'language_code': lang.lang,
                'language_name': LANGUAGE_NAMES.get(lang.lang, lang.lang.title()),
                'confidence': round(lang.prob, 4)
            })
        
        # Check if confidence meets threshold
        confidence = all_languages[0].prob
        if confidence < threshold:
            return {
                'detected_language': 'unknown',
                'confidence': confidence,
                'all_languages': languages_list,
                'success': False,
                'message': f"Confidence {confidence:.2f} below threshold {threshold}"
            }
        
        return {
            'detected_language': detected_lang,
            'confidence': confidence,
            'all_languages': languages_list,
            'success': True,
            'message': None
        }
        
    except LangDetectException as e:
        return {
            'detected_language': 'unknown',
            'confidence': 0.0,
            'all_languages': [],
            'success': False,
            'message': f"Language detection error: {str(e)}"
        }
    except Exception as e:
        return {
            'detected_language': 'unknown',
            'confidence': 0.0,
            'all_languages': [],
            'success': False,
            'message': f"Unexpected error: {str(e)}"
        }

def save_detection_history(text: str, result: Dict[str, Any]):
    """Save detection result to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO detection_history 
        (input_text, detected_language, confidence, all_languages)
        VALUES (?, ?, ?, ?)
    ''', (
        text,
        result['detected_language'],
        result['confidence'],
        json.dumps(result['all_languages'])
    ))
    
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/detect", response_model=DetectionResponse)
async def detect_language(request: DetectionRequest):
    """Detect language of a single text"""
    result = detect_language_with_confidence(request.text, request.threshold)
    save_detection_history(request.text, result)
    return DetectionResponse(**result)

@app.post("/detect/batch")
async def detect_language_batch(request: BatchDetectionRequest):
    """Detect languages for multiple texts"""
    results = []
    for text in request.texts:
        result = detect_language_with_confidence(text, request.threshold)
        save_detection_history(text, result)
        results.append({
            'text': text,
            'result': result
        })
    return {"results": results}

@app.get("/samples")
async def get_language_samples():
    """Get sample texts for different languages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT text, language_code, language_name FROM language_samples')
    samples = cursor.fetchall()
    conn.close()
    
    return {"samples": [
        {"text": sample[0], "language_code": sample[1], "language_name": sample[2]}
        for sample in samples
    ]}

@app.get("/stats", response_model=LanguageStats)
async def get_detection_stats():
    """Get detection statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total detections
    cursor.execute('SELECT COUNT(*) FROM detection_history')
    total_detections = cursor.fetchone()[0]
    
    # Most common language
    cursor.execute('''
        SELECT detected_language, COUNT(*) as count 
        FROM detection_history 
        GROUP BY detected_language 
        ORDER BY count DESC 
        LIMIT 1
    ''')
    most_common = cursor.fetchone()
    most_common_language = most_common[0] if most_common else "unknown"
    
    # Average confidence
    cursor.execute('SELECT AVG(confidence) FROM detection_history')
    avg_confidence = cursor.fetchone()[0] or 0.0
    
    # Languages detected count
    cursor.execute('''
        SELECT detected_language, COUNT(*) as count 
        FROM detection_history 
        GROUP BY detected_language
    ''')
    languages_detected = dict(cursor.fetchall())
    
    conn.close()
    
    return LanguageStats(
        total_detections=total_detections,
        most_common_language=most_common_language,
        average_confidence=round(avg_confidence, 4),
        languages_detected=languages_detected
    )

@app.get("/history")
async def get_detection_history(limit: int = 50):
    """Get recent detection history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT input_text, detected_language, confidence, all_languages, created_at
        FROM detection_history
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    history = cursor.fetchall()
    conn.close()
    
    return {"history": [
        {
            "text": item[0],
            "detected_language": item[1],
            "confidence": item[2],
            "all_languages": json.loads(item[3]),
            "created_at": item[4]
        }
        for item in history
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
