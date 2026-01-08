import asyncio
import websockets
import json
import threading
import time
from typing import Dict, Any

class AlexaIntegration:
    def __init__(self, luna_core):
        self.luna = luna_core
        self.server = None
        self.clients = set()
        self.enabled = False
        self.port = 8765
        
        # Carregar configurações
        self.load_config()
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.enabled = config['alexa']['enabled']
                self.port = config['alexa']['port']
        except:
            pass
    
    async def handle_client(self, websocket, path):
        """Manipula cliente WebSocket"""
        self.clients.add(websocket)
        print(f"🌐 Cliente Alexa conectado: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_alexa_command(data, websocket)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"🌐 Cliente Alexa desconectado")
        finally:
            self.clients.remove(websocket)
    
    async def process_alexa_command(self, data: Dict[str, Any], websocket):
        """Processa comando da Alexa"""
        command = data.get('command', '').lower()
        response = {'status': 'ok', 'response': ''}
        
        # Mapear comandos da Alexa para funcionalidades da Luna
        if 'luna' in command or 'assistente' in command:
            if 'como você está' in command or 'tudo bem' in command:
                response['response'] = self.luna.get_emotional_status()
            
            elif 'hora' in command:
                from datetime import datetime
                hora = datetime.now().strftime("%H:%M")
                response['response'] = f"São {hora}"
            
            elif 'data' in command:
                from datetime import datetime
                data_atual = datetime.now().strftime("%d/%m/%Y")
                response['response'] = f"Hoje é {data_atual}"
            
            elif 'amor' in command or 'gosta' in command:
                love_status = self.luna.get_love_status()
                response['response'] = f"Eu estou me sentindo {love_status}"
            
            elif 'sistema' in command or 'computador' in command:
                sys_info = self.luna.get_system_info()
                response['response'] = f"Sistema com {sys_info['cpu_percent']}% de CPU"
            
            else:
                response['response'] = "Comando recebido, mas não entendi completamente"
        
        await websocket.send(json.dumps(response))
    
    async def send_to_alexa(self, message: str):
        """Envia mensagem para todos os clientes Alexa"""
        if not self.clients:
            return
        
        data = {
            'from': 'luna',
            'message': message,
            'timestamp': time.time()
        }
        
        for client in self.clients:
            try:
                await client.send(json.dumps(data))
            except:
                pass
    
    async def start_server(self):
        """Inicia servidor WebSocket"""
        self.server = await websockets.serve(
            self.handle_client,
            "0.0.0.0",  # Aceitar conexões de qualquer IP
            self.port
        )
        print(f"🌐 Servidor Alexa iniciado na porta {self.port}")
        
        await self.server.wait_closed()
    
    def run_server(self):
        """Executa servidor em thread separada"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_server())
    
    def start(self):
        """Inicia integração com Alexa"""
        if not self.enabled:
            return
        
        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True
        server_thread.start()
        print("✅ Integração Alexa ativada")
    
    def stop(self):
        """Para integração com Alexa"""
        if self.server:
            self.server.close()