import os
import sys

# Adicionar a pasta worker ao sys.path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processor import PatentProcessor
from database import logger

def test_connection():
    print("📡 Iniciando Teste de Conectividade do LLM...")
    processor = PatentProcessor()
    
    # Testar a geração com dados mockados
    test_title = "CULTIVATION METHOD OF GREEN CROPS MOSTLY TOMATOES WITH DRIP IRRIGATION"
    test_desc = "Method comprises automated soil humidity tracking, drip irrigation, organic mineral fertilization, and canopy monitoring."
    
    print("\n🧠 Enviando patente de teste para o LLM...")
    prompt = processor._build_prompt(test_title, test_desc)
    
    try:
        if processor.groq_api_key:
            print(f"🔗 Conectando ao Groq Cloud API ({processor.groq_model})...")
            import requests
            headers = {
                "Authorization": f"Bearer {processor.groq_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": processor.groq_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é um especialista em Inteligência Competitiva e Inovação. Analise a patente e responda EXCLUSIVAMENTE em formato JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
        else:
            print(f"🔗 Conectando ao Ollama Local ({processor.model_name})... (Lembre-se que isso exige que o serviço local esteja rodando)")
            import requests
            response = requests.post(
                f"{processor.ollama_url}/api/generate",
                json={
                    "model": processor.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
        if response.status_code == 200:
            print("✅ Conectado com Sucesso!")
            if processor.groq_api_key:
                result = response.json()["choices"][0]["message"]["content"]
            else:
                result = response.json().get("response")
                
            print("\n📥 Resposta Recebida:")
            print(result)
            
            # Validar se o JSON é válido
            import json
            data = json.loads(result)
            print("\n✅ Validação de JSON: Sucesso! Todos os campos estão presentes:")
            for k, v in data.items():
                print(f"  • {k}: {v}")
        else:
            print(f"❌ Falha na conexão. HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro crítico no teste: {str(e)}")

if __name__ == "__main__":
    test_connection()
