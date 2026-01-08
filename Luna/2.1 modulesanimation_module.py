import pygame
import random
import math
import time
from dataclasses import dataclass
from typing import Tuple, List, Optional
import json

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    size: float
    color: Tuple[int, int, int]
    lifetime: float
    particle_type: str = "circle"

class LunaAnimation:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.SRCALPHA)
        pygame.display.set_caption("Luna - Assistente Virtual")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.particles = []
        self.luna_x = width // 2
        self.luna_y = height // 2
        self.luna_size = 50
        self.luna_color = (173, 216, 230)  # Azul claro
        self.luna_pulse = 0
        self.emotion = "neutral"
        self.mouse_interaction = True
        self.auto_animations = True
        
        # Estados emocionais
        self.emotion_colors = {
            "happy": (255, 255, 150),
            "neutral": (173, 216, 230),
            "sad": (150, 150, 255),
            "love": (255, 182, 193),
            "excited": (255, 105, 180),
            "thinking": (200, 230, 255)
        }
        
        # Carregar configurações
        self.load_config()
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.mouse_interaction = config['animation']['mouse_interaction']
                self.auto_animations = config['animation']['auto_animations']
        except:
            pass
    
    def update_emotion(self, emotion: str):
        """Atualiza emoção atual"""
        self.emotion = emotion
        if emotion in self.emotion_colors:
            self.luna_color = self.emotion_colors[emotion]
    
    def create_particle(self, x=None, y=None, emotion=None):
        """Cria partículas baseadas na emoção"""
        if x is None:
            x = self.luna_x
        if y is None:
            y = self.luna_y
        if emotion is None:
            emotion = self.emotion
        
        color_map = {
            "happy": (255, 255, 100),
            "love": (255, 182, 193, 180),
            "excited": (255, 105, 180, 200)
        }
        
        color = color_map.get(emotion, (255, 255, 255, 100))
        
        for _ in range(random.randint(3, 8)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=vx,
                    vy=vy,
                    size=random.uniform(2, 5),
                    color=color,
                    lifetime=random.uniform(30, 60)
                )
            )
    
    def draw_luna_gota(self):
        """Desenha Luna no formato de gota animada"""
        self.luna_pulse += 0.05
        
        # Base da gota
        points = []
        for i in range(36):
            angle = (i / 36) * 2 * math.pi
            radius = self.luna_size * (1 + 0.1 * math.sin(self.luna_pulse + i * 0.2))
            
            # Formato de gota (mais estreito na parte superior)
            if i < 18:
                radius *= 0.8
            
            x = self.luna_x + radius * math.cos(angle)
            y = self.luna_y + radius * math.sin(angle)
            points.append((x, y))
        
        # Desenhar gota com gradiente
        for i in range(len(points)):
            pygame.draw.line(
                self.screen,
                self.luna_color,
                points[i],
                points[(i + 1) % len(points)],
                3
            )
        
        # Preencher gota
        if len(points) >= 3:
            pygame.draw.polygon(
                self.screen,
                (*self.luna_color, 150),  # Com transparência
                points
            )
        
        # Olhos animados
        eye_offset = self.luna_size * 0.3
        eye_size = self.luna_size * 0.1
        
        left_eye_x = self.luna_x - eye_offset
        right_eye_x = self.luna_x + eye_offset
        eye_y = self.luna_y - eye_offset * 0.5
        
        # Piscar ocasionalmente
        blink = 1
        if random.random() < 0.002:  # 0.2% chance de piscar por frame
            blink = 0.1
        
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (int(left_eye_x), int(eye_y)),
            int(eye_size * blink)
        )
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (int(right_eye_x), int(eye_y)),
            int(eye_size * blink)
        )
        
        # Boca baseada na emoção
        mouth_y = self.luna_y + eye_offset * 0.5
        if self.emotion == "happy":
            pygame.draw.arc(
                self.screen,
                (0, 0, 0),
                (self.luna_x - eye_offset, mouth_y - eye_size, 
                 eye_offset * 2, eye_size * 2),
                0, math.pi,
                2
            )
        elif self.emotion == "love":
            # Coração pequeno
            heart_size = eye_size
            pygame.draw.polygon(
                self.screen,
                (255, 105, 180),
                [
                    (self.luna_x, mouth_y),
                    (self.luna_x - heart_size, mouth_y - heart_size),
                    (self.luna_x - heart_size * 0.5, mouth_y - heart_size * 1.5),
                    (self.luna_x, mouth_y - heart_size),
                    (self.luna_x + heart_size * 0.5, mouth_y - heart_size * 1.5),
                    (self.luna_x + heart_size, mouth_y - heart_size),
                ]
            )
    
    def draw_particles(self):
        """Desenha e atualiza partículas"""
        new_particles = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.05  # Gravidade leve
            p.lifetime -= 1
            
            if p.lifetime > 0:
                new_particles.append(p)
                
                # Desenhar partícula
                alpha = int(255 * (p.lifetime / 60))
                if p.particle_type == "circle":
                    pygame.draw.circle(
                        self.screen,
                        (*p.color[:3], alpha),
                        (int(p.x), int(p.y)),
                        int(p.size)
                    )
        
        self.particles = new_particles
    
    def handle_mouse(self, pos):
        """Interação com mouse"""
        if not self.mouse_interaction:
            return
        
        mouse_x, mouse_y = pos
        distance = math.sqrt((mouse_x - self.luna_x)**2 + (mouse_y - self.luna_y)**2)
        
        if distance < 100:
            # Repulsão suave
            angle = math.atan2(mouse_y - self.luna_y, mouse_x - self.luna_x)
            force = min(5, 100 / (distance + 1))
            self.luna_x -= math.cos(angle) * force
            self.luna_y -= math.sin(angle) * force
            
            # Criar partículas de interação
            if random.random() < 0.3:
                self.create_particle(mouse_x, mouse_y, "excited")
    
    def update(self):
        """Atualiza animação"""
        self.screen.fill((25, 25, 40, 0))  # Fundo escuro semi-transparente
        
        # Animações automáticas
        if self.auto_animations:
            if random.random() < 0.01:
                self.create_particle(emotion=self.emotion)
            
            # Movimento suave aleatório
            self.luna_x += random.uniform(-0.5, 0.5)
            self.luna_y += random.uniform(-0.5, 0.5)
            
            # Manter dentro dos limites
            self.luna_x = max(self.luna_size, min(self.width - self.luna_size, self.luna_x))
            self.luna_y = max(self.luna_size, min(self.height - self.luna_size, self.luna_y))
        
        # Desenhar elementos
        self.draw_particles()
        self.draw_luna_gota()
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def run(self):
        """Loop principal da animação"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.update()
        
        pygame.quit()