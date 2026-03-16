import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

class SystemAnalyzer:
    def __init__(self):
        # Cargar variables de entorno desde la raíz del proyecto
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key and api_key != "tu_api_key_aqui" else None

    def analyze_critical_state(self, metrics: dict, logs: str) -> dict:
        if not self.client:
            return {"error": "API Key de Gemini no configurada en el archivo .env"}

        SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE).
Your task is to analyze system metrics and logs to identify the root cause of performance issues or anomalies.
You must provide your analysis and recommendations strictly in JSON format.
The JSON should have the following structure:
{
  "issue_detected": "Brief description of the issue",
  "root_cause": "Detailed analysis of what is causing the problem based on metrics and logs",
  "recommendations": ["Actionable step 1", "Actionable step 2"]
}
"""

        prompt = f"""System Metrics:
{json.dumps(metrics, indent=2)}

Recent Logs:
{logs}

Please analyze this data."""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Error al procesar la respuesta JSON de Gemini", "raw_response": response.text}
        except Exception as e:
            return {"error": f"Error al comunicarse con la API de Gemini: {e}"}
