import psutil
import time
import json
import threading
import os
from datetime import datetime
from typing import List, Dict, Any
import winreg  # Windows only
import subprocess

class SystemMonitor:
    def __init__(self):
        self.usb_devices = {}
        self.drivers = {}
        self.monitoring = False
        self.callbacks = []
        
        # Carregar configurações
        self.load_config()
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {}
    
    def get_usb_devices(self):
        """Obtém dispositivos USB conectados"""
        devices = []
        
        try:
            # Windows - via Registry
            access_reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(access_reg, r"SYSTEM\CurrentControlSet\Enum\USB")
            
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    for j in range(winreg.QueryInfoKey(subkey)[0]):
                        try:
                            device_key_name = winreg.EnumKey(subkey, j)
                            device_key = winreg.OpenKey(subkey, device_key_name)
                            
                            try:
                                device_desc = winreg.QueryValueEx(device_key, "DeviceDesc")[0]
                                if isinstance(device_desc, bytes):
                                    device_desc = device_desc.decode('utf-8', errors='ignore')
                                
                                devices.append({
                                    'id': f"{subkey_name}_{device_key_name}",
                                    'description': device_desc,
                                    'connected': True,
                                    'first_seen': datetime.now().isoformat()
                                })
                            finally:
                                winreg.CloseKey(device_key)
                        except:
                            continue
                finally:
                    winreg.CloseKey(subkey)
                    
        except:
            # Fallback para sistemas não-Windows ou se Registry falhar
            for disk in psutil.disk_partitions():
                if 'removable' in disk.opts or 'usb' in disk.device.lower():
                    devices.append({
                        'id': disk.device,
                        'description': disk.mountpoint,
                        'connected': True,
                        'first_seen': datetime.now().isoformat()
                    })
        
        return devices
    
    def get_drivers_info(self):
        """Obtém informações sobre drivers"""
        drivers = []
        
        try:
            # Windows - lista drivers via WMIC
            result = subprocess.run(
                ['wmic', 'path', 'win32_pnpentity', 'get', 'name,status'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.strip().rsplit('  ', 1)
                    if len(parts) == 2:
                        name, status = parts
                        drivers.append({
                            'name': name.strip(),
                            'status': status.strip(),
                            'last_check': datetime.now().isoformat()
                        })
        except:
            # Simular dados para outros sistemas
            drivers = [
                {'name': 'Driver Simulado 1', 'status': 'OK', 'last_check': datetime.now().isoformat()},
                {'name': 'Driver Simulado 2', 'status': 'OK', 'last_check': datetime.now().isoformat()}
            ]
        
        return drivers
    
    def monitor_usb_changes(self):
        """Monitora mudanças em dispositivos USB"""
        previous_devices = {}
        
        while self.monitoring:
            current_devices = {d['id']: d for d in self.get_usb_devices()}
            
            # Verificar novos dispositivos
            for device_id, device in current_devices.items():
                if device_id not in previous_devices:
                    print(f"🆕 Novo dispositivo USB: {device['description']}")
                    self.notify_callbacks('usb_connected', device)
            
            # Verificar dispositivos removidos
            for device_id, device in previous_devices.items():
                if device_id not in current_devices:
                    print(f"❌ Dispositivo USB removido: {device['description']}")
                    self.notify_callbacks('usb_disconnected', device)
            
            previous_devices = current_devices
            time.sleep(2)  # Verificar a cada 2 segundos
    
    def monitor_drivers(self):
        """Monitora status de drivers"""
        previous_status = {}
        
        while self.monitoring:
            current_drivers = self.get_drivers_info()
            current_status = {d['name']: d['status'] for d in current_drivers}
            
            for driver_name, status in current_status.items():
                if driver_name in previous_status:
                    if previous_status[driver_name] != status:
                        print(f"⚠️ Driver alterado: {driver_name} - {previous_status[driver_name]} -> {status}")
                        self.notify_callbacks('driver_changed', {
                            'name': driver_name,
                            'old_status': previous_status[driver_name],
                            'new_status': status
                        })
                
                previous_status[driver_name] = status
            
            time.sleep(5)  # Verificar a cada 5 segundos
    
    def notify_callbacks(self, event_type, data):
        """Notifica callbacks registrados"""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except:
                pass
    
    def register_callback(self, callback):
        """Registra callback para eventos"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Inicia monitoramento"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        # Iniciar threads de monitoramento
        if self.config.get('system', {}).get('monitor_usb', True):
            usb_thread = threading.Thread(target=self.monitor_usb_changes)
            usb_thread.daemon = True
            usb_thread.start()
        
        if self.config.get('system', {}).get('monitor_drivers', True):
            driver_thread = threading.Thread(target=self.monitor_drivers)
            driver_thread.daemon = True
            driver_thread.start()
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring = False
    
    def get_system_info(self):
        """Obtém informações do sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            'running_time': time.time() - psutil.boot_time()
        }