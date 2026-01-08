import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import threading
import time
import random
from PIL import Image, ImageTk
from datetime import datetime
import pygame
import webbrowser

# Importar módulos
sys.path.append('modules')
from animation_module import LunaAnimation
from voice_module import VoiceAssistant
from recognition_module import RecognitionSystem
from system_module import SystemMonitor
from alexa_module import AlexaIntegration

class LunaApp:
    def __init__(self):
        # Configurar CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("Luna - Assistente Virtual Inteligente")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Variáveis de estado
        self.luna_active = False
        self.animation_thread = None
        self.animation_running = False
        self.current_emotion = "neutral"
        self.love_level = 50
        
        # Inicializar módulos
        self.init_modules()
        
        # Carregar configurações
        self.load_config()
        
        # Configurar interface
        self.setup_ui()
        
        # Iniciar serviços em background
        self.start_background_services()
        
        # Proteger contra fechamento acidental
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_modules(self):
        """Inicializa todos os módulos"""
        self.voice = VoiceAssistant()
        self.recognition = RecognitionSystem()
        self.system = SystemMonitor()
        self.alexa = AlexaIntegration(self)
        
        # Registrar callback para eventos do sistema
        self.system.register_callback(self.handle_system_event)
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
                self.luna_active = self.config['luna']['active']
                self.love_level = self.config['emotions']['base_love']
        except:
            self.config = {
                "luna": {"active": False},
                "emotions": {"base_love": 50}
            }
    
    def save_config(self):
        """Salva configurações no arquivo"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ui(self):
        """Configura interface do usuário"""
        # Configurar grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Sidebar esquerda
        self.create_sidebar()
        
        # Área principal
        self.create_main_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_sidebar(self):
        """Cria sidebar esquerda"""
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)
        
        # Logo Luna
        logo_label = ctk.CTkLabel(
            sidebar,
            text="🌙 LUNA",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Botão Ativar/Desativar
        self.toggle_btn = ctk.CTkButton(
            sidebar,
            text="▶️ ATIVAR LUNA",
            command=self.toggle_luna,
            fg_color="#4CAF50" if not self.luna_active else "#F44336",
            hover_color="#45a049" if not self.luna_active else "#d32f2f",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.toggle_btn.grid(row=1, column=0, padx=20, pady=10)
        
        # Nível de Amor
        love_frame = ctk.CTkFrame(sidebar)
        love_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            love_frame,
            text="💖 Nível de Amor",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(5, 0))
        
        self.love_progress = ctk.CTkProgressBar(love_frame)
        self.love_progress.pack(padx=10, pady=5, fill="x")
        self.love_progress.set(self.love_level / 100)
        
        self.love_label = ctk.CTkLabel(
            love_frame,
            text=self.recognition.get_love_status().title(),
            font=ctk.CTkFont(size=12)
        )
        self.love_label.pack(pady=(0, 5))
        
        # Botões do menu
        menu_buttons = [
            ("🎭 Animação", self.show_animation_window),
            ("🎤 Voz", self.show_voice_settings),
            ("👤 Reconhecimento", self.show_recognition_window),
            ("🖥️ Sistema", self.show_system_monitor),
            ("🌐 Alexa", self.show_alexa_settings),
            ("⚙️ Configurações", self.show_settings_window),
            ("📊 Estatísticas", self.show_statistics),
            ("❓ Ajuda", self.show_help)
        ]
        
        for i, (text, command) in enumerate(menu_buttons, start=3):
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                command=command,
                height=40,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=i, column=0, padx=20, pady=2, sticky="ew")
    
    def create_main_area(self):
        """Cria área principal"""
        main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="Painel de Controle - Luna AI",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Área de animação/visualização
        self.animation_canvas = ctk.CTkCanvas(
            main_frame,
            bg="#1a1a2e",
            highlightthickness=0
        )
        self.animation_canvas.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Área de console
        console_frame = ctk.CTkFrame(main_frame)
        console_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        console_label = ctk.CTkLabel(
            console_frame,
            text="📝 Console de Atividades",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        console_label.pack(pady=(10, 5))
        
        self.console_text = ctk.CTkTextbox(
            console_frame,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.console_text.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.console_text.insert("1.0", "✅ Sistema Luna inicializado\n")
        self.console_text.configure(state="disabled")
    
    def create_status_bar(self):
        """Cria barra de status"""
        status_bar = ctk.CTkFrame(self.root, height=30)
        status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Status Luna
        self.status_label = ctk.CTkLabel(
            status_bar,
            text="🟢 Luna: Ativa" if self.luna_active else "🔴 Luna: Inativa",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=20)
        
        # Status voz
        self.voice_status = ctk.CTkLabel(
            status_bar,
            text="🎤 Voz: Ativa",
            font=ctk.CTkFont(size=12)
        )
        self.voice_status.pack(side="left", padx=20)
        
        # Status sistema
        self.system_status = ctk.CTkLabel(
            status_bar,
            text="🖥️ Sistema: Monitorando",
            font=ctk.CTkFont(size=12)
        )
        self.system_status.pack(side="left", padx=20)
        
        # Hora
        self.time_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.time_label.pack(side="right", padx=20)
        
        # Atualizar hora
        self.update_time()
    
    def update_time(self):
        """Atualiza hora na status bar"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"🕒 {current_time}")
        self.root.after(1000, self.update_time)
    
    def toggle_luna(self):
        """Ativa/desativa Luna"""
        self.luna_active = not self.luna_active
        
        if self.luna_active:
            self.toggle_btn.configure(
                text="⏸️ DESATIVAR LUNA",
                fg_color="#F44336",
                hover_color="#d32f2f"
            )
            self.status_label.configure(text="🟢 Luna: Ativa")
            self.log("Luna ativada")
            
            # Iniciar animação em thread separada
            if not self.animation_running:
                self.start_animation()
            
            # Iniciar reconhecimento de voz
            self.voice.start_listening_loop(self.process_voice_command)
            
        else:
            self.toggle_btn.configure(
                text="▶️ ATIVAR LUNA",
                fg_color="#4CAF50",
                hover_color="#45a049"
            )
            self.status_label.configure(text="🔴 Luna: Inativa")
            self.log("Luna desativada")
            
            # Parar animação
            self.stop_animation()
            
            # Parar reconhecimento de voz
            self.voice.stop_listening()
    
    def start_animation(self):
        """Inicia animação da Luna"""
        def animation_thread():
            self.animation_running = True
            luna_anim = LunaAnimation(400, 400)
            luna_anim.update_emotion(self.current_emotion)
            luna_anim.run()
        
        self.animation_thread = threading.Thread(target=animation_thread)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def stop_animation(self):
        """Para animação da Luna"""
        self.animation_running = False
    
    def process_voice_command(self, command):
        """Processa comando de voz"""
        self.log(f"Comando de voz: {command}")
        
        # Analisar emoção no comando
        emotion = self.recognition.analyze_emotion(command)
        self.current_emotion = emotion
        
        # Atualizar nível de amor
        self.update_love_display()
        
        # Responder ao comando
        responses = {
            "hello": ["Olá! Como você está?", "Oi! Tudo bem?", "Olá, estou aqui!"],
            "how are you": ["Estou bem, obrigada!", "Me sinto ótima hoje!", "Estou feliz em te ver!"],
            "love you": ["Eu também te amo!", "Isso me deixa tão feliz!", "Meu coração está quentinho!"],
            "time": [f"Agora são {datetime.now().strftime('%H:%M')}", f"O relógio marca {datetime.now().strftime('%H:%M:%S')}"],
            "date": [f"Hoje é {datetime.now().strftime('%d/%m/%Y')}", f"Estamos no dia {datetime.now().strftime('%d de %B de %Y')}"]
        }
        
        # Encontrar resposta apropriada
        response = None
        for key, possible_responses in responses.items():
            if key in command.lower():
                response = random.choice(possible_responses)
                break
        
        if not response:
            response = "Desculpe, não entendi. Pode repetir?"
        
        # Falar resposta
        self.voice.speak(response, emotion)
        self.log(f"Luna respondeu: {response}")
    
    def update_love_display(self):
        """Atualiza display do nível de amor"""
        self.love_level = self.recognition.love_level
        self.love_progress.set(self.love_level / 100)
        self.love_label.configure(
            text=self.recognition.get_love_status().title()
        )
    
    def handle_system_event(self, event_type, data):
        """Lida com eventos do sistema"""
        if event_type == 'usb_connected':
            message = f"🔌 USB conectado: {data['description']}"
        elif event_type == 'usb_disconnected':
            message = f"🔌 USB desconectado: {data['description']}"
        elif event_type == 'driver_changed':
            message = f"⚠️ Driver alterado: {data['name']}"
        else:
            message = f"📡 Evento do sistema: {event_type}"
        
        self.log(message)
        
        # Se Luna estiver ativa, notificar por voz
        if self.luna_active:
            self.voice.speak(f"Evento do sistema: {message.split(': ')[1]}", "neutral")
    
    def log(self, message):
        """Adiciona mensagem ao console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_text.configure(state="normal")
        self.console_text.insert("end", f"[{timestamp}] {message}\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")
    
    def show_animation_window(self):
        """Mostra janela de animação"""
        window = ctk.CTkToplevel(self.root)
        window.title("🎭 Configurações de Animação")
        window.geometry("500x400")
        
        # Centralizar
        window.transient(self.root)
        window.grab_set()
        
        # Conteúdo
        ctk.CTkLabel(
            window,
            text="Configurações de Animação",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Opções de animação
        options = [
            ("Animações automáticas", True),
            ("Efeitos de partículas", True),
            ("Interações com mouse", True),
            ("Física realista", False),
            ("Sombras e iluminação", False)
        ]
        
        for text, default in options:
            var = ctk.BooleanVar(value=default)
            cb = ctk.CTkCheckBox(window, text=text, variable=var)
            cb.pack(pady=5, padx=20, anchor="w")
    
    def show_voice_settings(self):
        """Mostra configurações de voz"""
        window = ctk.CTkToplevel(self.root)
        window.title("🎤 Configurações de Voz")
        window.geometry("500x400")
        
        ctk.CTkLabel(
            window,
            text="Configurações de Voz",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Teste de voz
        test_frame = ctk.CTkFrame(window)
        test_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(test_frame, text="Teste de Voz:").pack(side="left", padx=10)
        
        test_entry = ctk.CTkEntry(test_frame, placeholder_text="Digite algo para testar")
        test_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        def test_voice():
            text = test_entry.get()
            if text:
                self.voice.speak(text, "neutral")
        
        ctk.CTkButton(test_frame, text="Falar", command=test_voice).pack(side="left", padx=5)
    
    def show_recognition_window(self):
        """Mostra janela de reconhecimento"""
        window = ctk.CTkToplevel(self.root)
        window.title("👤 Reconhecimento de Usuário")
        window.geometry("600x500")
        
        # Abas
        tabview = ctk.CTkTabview(window)
        tabview.pack(pady=20, padx=20, fill="both", expand=True)
        
        tabview.add("Voz")
        tabview.add("Emoções")
        tabview.add("Usuários")
        
        # Aba Voz
        ctk.CTkLabel(
            tabview.tab("Voz"),
            text="Perfis de Voz Reconhecidos"
        ).pack(pady=10)
        
        # Lista de vozes
        voices_text = ctk.CTkTextbox(tabview.tab("Voz"), height=200)
        voices_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        for voice_hash, data in self.recognition.voice_profiles.items():
            voices_text.insert("end", f"Voz {voice_hash[:8]}...\n")
        
        # Aba Emoções
        emotions = ["feliz", "triste", "amor", "excitado", "neutro"]
        for emotion in emotions:
            btn = ctk.CTkButton(
                tabview.tab("Emoções"),
                text=f"Testar: {emotion}",
                command=lambda e=emotion: self.test_emotion(e)
            )
            btn.pack(pady=5)
    
    def show_system_monitor(self):
        """Mostra monitor do sistema"""
        window = ctk.CTkToplevel(self.root)
        window.title("🖥️ Monitor do Sistema")
        window.geometry("700x500")
        
        # Atualizar informações do sistema
        def update_info():
            sys_info = self.system.get_system_info()
            info_text = f"""
            CPU: {sys_info['cpu_percent']}%
            Memória: {sys_info['memory_percent']}%
            Disco: {sys_info['disk_usage']}%
            Tempo ligado: {int(sys_info['running_time'] / 3600)} horas
            
            Dispositivos USB: {len(self.system.get_usb_devices())}
            Drivers: {len(self.system.get_drivers_info())}
            """
            
            info_label.configure(text=info_text)
            window.after(2000, update_info)
        
        ctk.CTkLabel(
            window,
            text="Monitor do Sistema em Tempo Real",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        info_label = ctk.CTkLabel(window, text="", font=ctk.CTkFont(size=14))
        info_label.pack(pady=10)
        
        update_info()
    
    def show_alexa_settings(self):
        """Mostra configurações da Alexa"""
        window = ctk.CTkToplevel(self.root)
        window.title("🌐 Integração com Alexa")
        window.geometry("500x400")
        
        ctk.CTkLabel(
            window,
            text="Configurações da Alexa",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Ativar/Desativar
        alexa_var = ctk.BooleanVar(value=self.alexa.enabled)
        
        def toggle_alexa():
            self.alexa.enabled = alexa_var.get()
            if self.alexa.enabled:
                self.alexa.start()
                self.log("Integração Alexa ativada")
            else:
                self.alexa.stop()
                self.log("Integração Alexa desativada")
        
        ctk.CTkCheckBox(
            window,
            text="Ativar integração com Alexa",
            variable=alexa_var,
            command=toggle_alexa
        ).pack(pady=10)
        
        ctk.CTkLabel(
            window,
            text=f"Servidor WebSocket na porta: {self.alexa.port}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
    
    def show_settings_window(self):
        """Mostra janela de configurações gerais"""
        window = ctk.CTkToplevel(self.root)
        window.title("⚙️ Configurações Gerais")
        window.geometry("600x500")
        
        # Notebook para abas
        tabview = ctk.CTkTabview(window)
        tabview.pack(pady=20, padx=20, fill="both", expand=True)
        
        tabview.add("Geral")
        tabview.add("Sistema")
        tabview.add("Segurança")
        
        # Aba Geral
        general_options = [
            ("Iniciar com Windows", False),
            ("Sempre no topo", True),
            ("Minimizar para bandeja", True),
            ("Notificações por voz", True),
            ("Animações automáticas", True)
        ]
        
        for text, default in general_options:
            var = ctk.BooleanVar(value=default)
            cb = ctk.CTkCheckBox(tabview.tab("Geral"), text=text, variable=var)
            cb.pack(pady=2, padx=20, anchor="w")
    
    def show_statistics(self):
        """Mostra estatísticas"""
        window = ctk.CTkToplevel(self.root)
        window.title("📊 Estatísticas da Luna")
        window.geometry("500x400")
        
        stats = f"""
        ⭐ Estatísticas da Luna ⭐
        
        Nível de Amor: {self.love_level}/100
        Status: {self.recognition.get_love_status()}
        
        Vozes Reconhecidas: {len(self.recognition.voice_profiles)}
        Usuários Registrados: {len(self.recognition.user_profiles)}
        
        Dispositivos USB Detectados: {len(self.system.usb_devices)}
        Drivers Monitorados: {len(self.system.drivers)}
        
        Tempo de Atividade: {self.get_uptime()}
        """
        
        ctk.CTkLabel(
            window,
            text=stats,
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(pady=40, padx=40)
    
    def show_help(self):
        """Mostra ajuda"""
        help_text = """
        🤖 Luna - Assistente Virtual Inteligente
        
        Comandos de Voz:
        - "Luna" + comando
        - "Luna, que horas são?"
        - "Luna, qual a data?"
        - "Luna, como você está?"
        
        Funcionalidades:
        1. Reconhecimento de voz
        2. Análise emocional
        3. Monitoramento de sistema
        4. Integração com Alexa
        5. Animação interativa
        
        Configuração:
        - Clique nos botões da sidebar para acessar
        diferentes configurações
        - Use o botão Ativar/Desativar para controlar Luna
        
        Suporte:
        Para mais ajuda, consulte a documentação.
        """
        
        messagebox.showinfo("Ajuda - Luna", help_text)
    
    def get_uptime(self):
        """Calcula tempo de atividade"""
        # Simulado - em produção calcularia tempo real
        return "1 hora 23 minutos"
    
    def start_background_services(self):
        """Inicia serviços em background"""
        # Iniciar monitoramento do sistema
        self.system.start_monitoring()
        
        # Iniciar integração Alexa
        self.alexa.start()
        
        # Iniciar atualização periódica
        self.periodic_update()
    
    def periodic_update(self):
        """Atualizações periódicas"""
        # Atualizar nível de amor
        self.update_love_display()
        
        # Verificar por atualizações
        self.check_updates()
        
        # Agendar próxima atualização
        self.root.after(30000, self.periodic_update)  # A cada 30 segundos
    
    def check_updates(self):
        """Verifica atualizações"""
        # Simulado - em produção faria check real
        pass
    
    def on_closing(self):
        """Lida com fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            # Parar todos os serviços
            self.luna_active = False
            self.voice.stop_listening()
            self.system.stop_monitoring()
            self.alexa.stop()
            
            # Salvar configurações
            self.save_config()
            
            # Fechar aplicação
            self.root.destroy()
    
    def run(self):
        """Executa aplicação"""
        self.root.mainloop()

def main():
    """Função principal"""
    print("🚀 Inicializando Luna AI...")
    
    # Verificar e criar estrutura de pastas
    os.makedirs('data/voices', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)
    
    # Iniciar aplicação
    app = LunaApp()
    app.run()

if __name__ == "__main__":
    main()