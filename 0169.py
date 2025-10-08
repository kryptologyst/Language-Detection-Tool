#!/usr/bin/env python3
"""
Project 169: Language Detection Tool - CLI Version
A simple command-line interface for language detection using langdetect.

This is the original CLI version. For the full web application with API,
database, and modern UI, see main.py and the templates directory.

Usage:
    python 0169.py
    python 0169.py "Your text here"
"""

import sys
from langdetect import detect, detect_langs, LangDetectException

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

def detect_language_cli(text):
    """Detect language with CLI-friendly output"""
    try:
        if not text.strip():
            print("❌ Error: Empty text provided")
            return
        
        detected_lang = detect(text)
        all_languages = detect_langs(text)
        
        # Get language name
        lang_name = LANGUAGE_NAMES.get(detected_lang, detected_lang.title())
        
        print(f"📝 Text: {text}")
        print(f"🔍 Detected Language: {lang_name} ({detected_lang})")
        print(f"📊 Confidence: {all_languages[0].prob:.2%}")
        
        if len(all_languages) > 1:
            print("\n📋 All detected languages:")
            for i, lang in enumerate(all_languages[:5], 1):  # Show top 5
                name = LANGUAGE_NAMES.get(lang.lang, lang.lang.title())
                print(f"  {i}. {name} ({lang.lang}): {lang.prob:.2%}")
        
        print("-" * 50)
        
    except LangDetectException as e:
        print(f"❌ Language detection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main CLI function"""
    print("🧠 Language Detection Tool - CLI Version")
    print("=" * 50)
    
    # Check if text provided as command line argument
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        detect_language_cli(text)
        return
    
    # Sample texts for demonstration
    sample_texts = [
        "This is an English sentence.",
        "Ceci est une phrase française.",
        "Dies ist ein deutscher Satz.",
        "これは日本語の文章です。",
        "Esto es una oración en español.",
        "Это предложение на русском языке.",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?",
        "こんにちは、元気ですか？",
        "안녕하세요, 어떻게 지내세요?"
    ]
    
    print("🔍 Detecting languages for sample texts:\n")
    
    for i, text in enumerate(sample_texts, 1):
        print(f"Sample {i}:")
        detect_language_cli(text)
    
    print("\n💡 Usage:")
    print("  python 0169.py                    # Run with sample texts")
    print("  python 0169.py 'Your text here'    # Detect specific text")
    print("\n🌐 For the full web application with API and database:")
    print("  python main.py                     # Start web server")
    print("  Then visit: http://localhost:8000")

if __name__ == "__main__":
    main()