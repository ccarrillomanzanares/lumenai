import time
import requests
import os
from dotenv import load_dotenv
from collector import SystemCollector

load_dotenv()

SERVER_URL = "http://localhost:8000"
AGENT_SECRET = os.getenv("AGENT_SECRET", "default-agent-secret")

def get_token():
    url = f"{SERVER_URL}/auth/token"
    try:
        response = requests.post(url, json={"agent_secret": AGENT_SECRET})
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error obteniendo token de acceso: {e}")
        return None

def run_agent():
    token = get_token()
    if not token:
        print("No se pudo obtener el token JWT, reintentando en 5s...")
        time.sleep(5)
        return run_agent() # Retry mechanism
        
    headers = {"Authorization": f"Bearer {token}"}
    collector = SystemCollector()
    print(f"Iniciando Agente LumenAI. Enviando métricas a {SERVER_URL}/metrics...")
    try:
        while True:
            data = collector.collect()
            try:
                response = requests.post(f"{SERVER_URL}/metrics", json=data, headers=headers)
                if response.status_code == 200:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Métricas enviadas. CPU: {data['metrics']['cpu_percent']}% | Status: {response.json().get('status', 'OK')}")
                elif response.status_code == 401:
                    print("Token expirado o inválido. Renovando token...")
                    return run_agent() # Renew token by restarting loop
                else:
                    print(f"Error del servidor HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error conectando al servidor: {e}")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nAgente detenido.")

if __name__ == "__main__":
    run_agent()
