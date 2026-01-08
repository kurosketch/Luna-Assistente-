import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import json
import os
from datetime import datetime
import wave
import pyaudio

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        
        # Configurar voz
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'brazil' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        
        # Fila de comandos
        self.command_queue = queue.Queue()
        self.listening = False
        self.wake_word = "luna"
        
        # Configurações
        self.voice_recognition = True
        self.record_unknown = True
        
        # Carregar configurações
        self.load_config()
        
        # Criar pasta de vozes se não existir
        os.makedirs('data/voices', exist_ok=True)
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.voice_recognition = config['voice']['voice_recognition']
                self.record_unknown = config['voice']['record_unknown_voices']
                self.wake_word = config['voice']['wake_word']
        except:
            pass
    
    def speak(self, text, emotion="neutral"):
        """Fala o texto com emoção"""
        if not self.engine:
            return
        
        # Ajustar velocidade baseado na emoção
        speed_map = {
            "excited": 220,
            "happy": 200,
            "neutral": 180,
            "sad": 150,
            "love": 170
        }
        
        self.engine.setProperty('rate', speed_map.get(emotion, 180))
        
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
        
        thread = threading.Thread(target=_speak)
        thread.start()
        return thread
    
    def listen(self, timeout=5, phrase_time_limit=None):
        """Escuta por comandos"""
        if not self.voice_recognition:
            return None
        
        with self.microphone as source:
            print("🎤 Escutando...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                text = self.recognizer.recognize_google(audio, language='pt-BR')
                print(f"📝 Reconhecido: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("❌ Não entendi")
                return None
            except sr.RequestError:
                print("❌ Erro no serviço de reconhecimento")
                return None
    
    def record_unknown_voice(self, audio_data):
        """Grava voz desconhecida para análise futura"""
        if not self.record_unknown:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/voices/unknown_{timestamp}.wav"
        
        # Converter audio_data para WAV
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(audio_data.get_wav_data())
        
        print(f"📼 Voz gravada: {filename}")
    
    def start_listening_loop(self, callback):
        """Inicia loop de escuta contínua"""
        self.listening = True
        
        def listen_loop():
            while self.listening:
                command = self.listen(timeout=3)
                if command:
                    if self.wake_word in command:
                        # Remover wake word
                        command = command.replace(self.wake_word, '').strip()
                        if command:
                            callback(command)
                    else:
                        # Comando sem wake word - gravar para análise
                        if self.record_unknown:
                            print(f"🗣️ Voz desconhecida detectada: {command}")
        
        thread = threading.Thread(target=listen_loop)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        """Para o loop de escuta"""
        self.listening = False