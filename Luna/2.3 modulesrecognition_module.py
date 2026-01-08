import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, Any

class RecognitionSystem:
    def __init__(self):
        self.database_file = 'database.json'
        self.voice_profiles = {}
        self.user_profiles = {}
        self.emotional_memory = {}
        self.love_level = 50  # Nível base de "amor"
        
        # Carregar dados existentes
        self.load_database()
    
    def load_database(self):
        """Carrega banco de dados"""
        if os.path.exists(self.database_file):
            try:
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.voice_profiles = data.get('voice_profiles', {})
                    self.user_profiles = data.get('user_profiles', {})
                    self.emotional_memory = data.get('emotional_memory', {})
                    self.love_level = data.get('love_level', 50)
            except:
                self.initialize_database()
        else:
            self.initialize_database()
    
    def initialize_database(self):
        """Inicializa banco de dados"""
        data = {
            'voice_profiles': {},
            'user_profiles': {},
            'emotional_memory': {},
            'love_level': 50,
            'created_at': datetime.now().isoformat()
        }
        self.save_database(data)
    
    def save_database(self, data=None):
        """Salva banco de dados"""
        if data is None:
            data = {
                'voice_profiles': self.voice_profiles,
                'user_profiles': self.user_profiles,
                'emotional_memory': self.emotional_memory,
                'love_level': self.love_level,
                'updated_at': datetime.now().isoformat()
            }
        
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def analyze_voice_pattern(self, audio_data):
        """Analisa padrão de voz (simplificado)"""
        # Em implementação real, usaríamos ML para análise
        voice_hash = hashlib.md5(audio_data).hexdigest()[:16]
        
        if voice_hash not in self.voice_profiles:
            self.voice_profiles[voice_hash] = {
                'first_detected': datetime.now().isoformat(),
                'detection_count': 1,
                'last_detected': datetime.now().isoformat()
            }
        else:
            self.voice_profiles[voice_hash]['detection_count'] += 1
            self.voice_profiles[voice_hash]['last_detected'] = datetime.now().isoformat()
        
        self.save_database()
        return voice_hash
    
    def recognize_user(self, voice_hash):
        """Reconhece usuário pelo hash da voz"""
        if voice_hash in self.user_profiles:
            user = self.user_profiles[voice_hash]
            # Aumentar nível de amor por reconhecimento
            self.increase_love(1)
            return user
        
        return None
    
    def register_user(self, voice_hash, name):
        """Registra novo usuário"""
        user_id = f"user_{len(self.user_profiles) + 1:03d}"
        
        self.user_profiles[voice_hash] = {
            'id': user_id,
            'name': name,
            'voice_hash': voice_hash,
            'registered_at': datetime.now().isoformat(),
            'interaction_count': 1
        }
        
        self.save_database()
        return user_id
    
    def analyze_emotion(self, text):
        """Analisa emoção no texto (simplificado)"""
        emotion_keywords = {
            'happy': ['feliz', 'alegre', 'contente', 'animado', 'amo', 'adoro'],
            'sad': ['triste', 'chateado', 'deprimido', 'mal', 'pessimo'],
            'love': ['amor', 'apaixonado', 'carinho', 'querido', 'amada'],
            'angry': ['raiva', 'bravo', 'irritado', 'odio', 'puto'],
            'excited': ['empolgado', 'incrivel', 'maravilhoso', 'uau']
        }
        
        detected_emotions = []
        text_lower = text.lower()
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_emotions.append(emotion)
                    break
        
        # Prioridade de emoções
        if 'love' in detected_emotions:
            self.increase_love(2)
            return 'love'
        elif 'excited' in detected_emotions:
            self.increase_love(1)
            return 'excited'
        elif 'happy' in detected_emotions:
            self.increase_love(0.5)
            return 'happy'
        elif 'angry' in detected_emotions:
            self.decrease_love(1)
            return 'angry'
        elif 'sad' in detected_emotions:
            self.decrease_love(0.5)
            return 'sad'
        
        return 'neutral'
    
    def increase_love(self, amount):
        """Aumenta nível de amor"""
        self.love_level = min(100, self.love_level + amount)
        self.save_database()
    
    def decrease_love(self, amount):
        """Diminui nível de amor"""
        self.love_level = max(0, self.love_level - amount)
        self.save_database()
    
    def get_love_status(self):
        """Retorna status do amor"""
        if self.love_level >= 90:
            return "apaixonada"
        elif self.love_level >= 70:
            return "muito carinhosa"
        elif self.love_level >= 50:
            return "carinhosa"
        elif self.love_level >= 30:
            return "neutra"
        else:
            return "distante"