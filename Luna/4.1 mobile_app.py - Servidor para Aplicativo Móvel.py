import socket
import threading
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

class MobileServer:
    def __init__(self, luna_core, port=8888):
        self.luna = luna_core
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
    
    def setup_routes(self):
        """Configura rotas da API"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            return jsonify({
                'status': 'online',
                'luna_active': self.luna.luna_active,
                'love_level': self.luna.love_level,
                'emotion': self.luna.current_emotion,
                'timestamp': time.time()
            })
        
        @self.app.route('/api/voice', methods=['POST'])
        def send_voice():
            data = request.json
            command = data.get('command', '')
            
            if command:
                self.luna.process_voice_command(command)
                return jsonify({'status': 'processed'})
            
            return jsonify({'status': 'error', 'message': 'No command'})
        
        @self.app.route('/api/speak', methods=['POST'])
        def speak():
            data = request.json
            text = data.get('text', '')
            emotion = data.get('emotion', 'neutral')
            
            if text:
                self.luna.voice.speak(text, emotion)
                return jsonify({'status': 'speaking'})
            
            return jsonify({'status': 'error'})
        
        @self.app.route('/api/system', methods=['GET'])
        def get_system_info():
            sys_info = self.luna.system.get_system_info()
            return jsonify(sys_info)
        
        @self.app.route('/api/toggle', methods=['POST'])
        def toggle_luna():
            self.luna.toggle_luna()
            return jsonify({'active': self.luna.luna_active})
    
    def start(self):
        """Inicia servidor móvel"""
        print(f"📱 Servidor móvel iniciado na porta {self.port}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)

# Adicionar no main.py
def init_mobile_server(luna_app):
    """Inicializa servidor para app móvel"""
    mobile = MobileServer(luna_app)
    mobile_thread = threading.Thread(target=mobile.start)
    mobile_thread.daemon = True
    mobile_thread.start()
    return mobile