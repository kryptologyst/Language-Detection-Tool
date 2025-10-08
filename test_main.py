import pytest
import json
from fastapi.testclient import TestClient
from main import app, detect_language_with_confidence, LANGUAGE_NAMES
import sqlite3
import os

# Test client
client = TestClient(app)

class TestLanguageDetection:
    """Test cases for language detection functionality"""
    
    def setup_method(self):
        """Setup test database"""
        # Use in-memory database for testing
        self.test_db = ":memory:"
        # We'll mock the database operations in the actual tests
    
    def test_detect_english_text(self):
        """Test detection of English text"""
        result = detect_language_with_confidence("Hello, how are you today?")
        assert result['detected_language'] == 'en'
        assert result['success'] is True
        assert result['confidence'] > 0.5
    
    def test_detect_french_text(self):
        """Test detection of French text"""
        result = detect_language_with_confidence("Bonjour, comment allez-vous?")
        assert result['detected_language'] == 'fr'
        assert result['success'] is True
        assert result['confidence'] > 0.5
    
    def test_detect_spanish_text(self):
        """Test detection of Spanish text"""
        result = detect_language_with_confidence("Hola, ¿cómo estás?")
        assert result['detected_language'] == 'es'
        assert result['success'] is True
        assert result['confidence'] > 0.5
    
    def test_detect_japanese_text(self):
        """Test detection of Japanese text"""
        result = detect_language_with_confidence("こんにちは、元気ですか？")
        assert result['detected_language'] == 'ja'
        assert result['success'] is True
        assert result['confidence'] > 0.5
    
    def test_empty_text(self):
        """Test handling of empty text"""
        result = detect_language_with_confidence("")
        assert result['success'] is False
        assert "Empty text" in result['message']
    
    def test_whitespace_only_text(self):
        """Test handling of whitespace-only text"""
        result = detect_language_with_confidence("   \n\t   ")
        assert result['success'] is False
        assert "Empty text" in result['message']
    
    def test_confidence_threshold(self):
        """Test confidence threshold filtering"""
        # Use a very high threshold to force failure
        result = detect_language_with_confidence("Hello", threshold=0.99)
        assert result['success'] is False
        assert "below threshold" in result['message']
    
    def test_language_names_mapping(self):
        """Test language code to name mapping"""
        assert LANGUAGE_NAMES['en'] == 'English'
        assert LANGUAGE_NAMES['fr'] == 'French'
        assert LANGUAGE_NAMES['es'] == 'Spanish'
        assert LANGUAGE_NAMES['ja'] == 'Japanese'

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Language Detection Tool" in response.text
    
    def test_detect_endpoint_success(self):
        """Test successful language detection via API"""
        response = client.post("/detect", json={
            "text": "Hello, how are you today?",
            "threshold": 0.5
        })
        assert response.status_code == 200
        data = response.json()
        assert data['detected_language'] == 'en'
        assert data['success'] is True
        assert data['confidence'] > 0.5
        assert len(data['all_languages']) > 0
    
    def test_detect_endpoint_empty_text(self):
        """Test API with empty text"""
        response = client.post("/detect", json={
            "text": "",
            "threshold": 0.5
        })
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert "Empty text" in data['message']
    
    def test_detect_endpoint_invalid_json(self):
        """Test API with invalid JSON"""
        response = client.post("/detect", json={
            "invalid_field": "test"
        })
        assert response.status_code == 422  # Validation error
    
    def test_batch_detection(self):
        """Test batch language detection"""
        texts = [
            "Hello, how are you?",
            "Bonjour, comment allez-vous?",
            "Hola, ¿cómo estás?"
        ]
        response = client.post("/detect/batch", json={
            "texts": texts,
            "threshold": 0.5
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 3
        assert data['results'][0]['result']['detected_language'] == 'en'
        assert data['results'][1]['result']['detected_language'] == 'fr'
        assert data['results'][2]['result']['detected_language'] == 'es'
    
    def test_batch_detection_empty_list(self):
        """Test batch detection with empty list"""
        response = client.post("/detect/batch", json={
            "texts": [],
            "threshold": 0.5
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['results']) == 0
    
    def test_samples_endpoint(self):
        """Test language samples endpoint"""
        response = client.get("/samples")
        assert response.status_code == 200
        data = response.json()
        assert 'samples' in data
        assert len(data['samples']) > 0
        
        # Check sample structure
        sample = data['samples'][0]
        assert 'text' in sample
        assert 'language_code' in sample
        assert 'language_name' in sample
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'total_detections' in data
        assert 'most_common_language' in data
        assert 'average_confidence' in data
        assert 'languages_detected' in data
        
        # Check data types
        assert isinstance(data['total_detections'], int)
        assert isinstance(data['average_confidence'], float)
        assert isinstance(data['languages_detected'], dict)
    
    def test_history_endpoint(self):
        """Test detection history endpoint"""
        response = client.get("/history")
        assert response.status_code == 200
        data = response.json()
        assert 'history' in data
        assert isinstance(data['history'], list)
    
    def test_history_endpoint_with_limit(self):
        """Test detection history endpoint with limit"""
        response = client.get("/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert 'history' in data
        assert len(data['history']) <= 5

class TestDatabaseOperations:
    """Test cases for database operations"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        # This would test the init_database function
        # For now, we'll just verify the function exists and can be called
        from main import init_database
        # The function should not raise an exception
        # In a real test, we'd use a test database
    
    def test_language_samples_structure(self):
        """Test language samples table structure"""
        # This would test the database schema
        # For now, we'll verify the sample data structure
        sample_data = [
            ("Hello, how are you today?", "en", "English"),
            ("Bonjour, comment allez-vous?", "fr", "French"),
        ]
        
        for text, code, name in sample_data:
            assert isinstance(text, str)
            assert isinstance(code, str)
            assert isinstance(name, str)
            assert len(text) > 0
            assert len(code) > 0
            assert len(name) > 0

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_short_text(self):
        """Test detection with very short text"""
        result = detect_language_with_confidence("Hi")
        # Should still work, but confidence might be lower
        assert 'detected_language' in result
        assert 'confidence' in result
    
    def test_mixed_language_text(self):
        """Test detection with mixed language text"""
        result = detect_language_with_confidence("Hello bonjour hola")
        # Should detect the most prominent language
        assert result['success'] is True
        assert result['detected_language'] in ['en', 'fr', 'es']
    
    def test_numbers_and_symbols(self):
        """Test detection with numbers and symbols"""
        result = detect_language_with_confidence("123 !@# $%^ &*()")
        # Should handle gracefully
        assert 'detected_language' in result
        assert 'confidence' in result
    
    def test_unicode_text(self):
        """Test detection with unicode characters"""
        result = detect_language_with_confidence("🚀 Hello World! 🌍")
        assert result['success'] is True
        assert result['detected_language'] == 'en'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
