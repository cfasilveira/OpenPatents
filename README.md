# OpenPatents 🚀

O **OpenPatents** é um ecossistema de inteligência competitiva projetado para minerar dados públicos de patentes e tecnologias expiradas, transformando descrições técnicas complexas em **oportunidades de negócio viáveis** para o cenário de 2026.

## 📋 Funcionalidades Principais

- **Extração Dinâmica:** Busca automática de patentes reais via **Europe PMC API** (Open Data).
- **Triagem por Nicho:** Pesquisa inteligente focada em Agro, Saúde, Pet, Energia, Mecânica, Logística e mais.
- **Inteligência Competitiva:** Análise profunda via **IA Local (Ollama + Mistral-Nemo)** que gera:
  - **Conceito de Negócio:** Tradução da patente para uma oportunidade de mercado.
  - **Insumos Modernos (2026):** Lista de materiais e tecnologias atuais para prototipagem.
  - **Métricas de Viabilidade:** Nível de investimento, complexidade de MVP e Time-to-Market.
- **Dashboard Real-time:** Interface moderna com atualização inteligente (Smart Refresh) que preserva a interação do usuário enquanto novas patentes são processadas.
- **Fonte Direta:** Link direto para a fonte original da patente para validação técnica.

## 🛠️ Stack Tecnológica

- **Backend:** FastAPI (Python 3.12+) - Alta performance e documentação automática.
- **Worker:** Processamento assíncrono para análise de IA pesada.
- **IA:** Ollama executando o modelo `mistral-nemo`.
- **Database:** PostgreSQL para persistência robusta.
- **Frontend:** Vite + Vanilla JS/CSS (Foco em performance e UX limpa).
- **Gerenciador de Pacotes:** `uv` (Astral) para Python e `npm` para Javascript.

## 📁 Estrutura do Projeto

- `/api`: Servidor FastAPI que gerencia a interface com o frontend e o banco de dados.
- `/worker`: Serviço responsável por minerar a API da Europe PMC e realizar as análises via Ollama.
- `/frontend`: Interface web moderna construída com Vite.
- `.env`: Configurações de ambiente (Banco de dados, URLs da API e IA).

## 🚀 Como Rodar o Ecossistema

### 1. Pré-requisitos
- **Ollama:** Instalado e rodando (`ollama run mistral-nemo`).
- **PostgreSQL:** Banco de dados ativo (via Docker ou local).
- **Python 3.12+** e **Node.js 18+**.

### 2. Configuração
Configure o arquivo `.env` na raiz do projeto:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/openpatents
OLLAMA_URL=http://localhost:11434
MODEL_NAME=mistral-nemo
```

### 3. Execução (3 terminais separados)

**Terminal 1: API**
```bash
cd api
uv run python main.py
```

**Terminal 2: Worker**
```bash
cd worker
uv run python main.py
```

**Terminal 3: Frontend**
```bash
cd frontend
npm install
npm run dev
```

Acesse o dashboard em `http://localhost:5173`.

---
*Desenvolvido para transformar ciência pública em inovação de mercado.*
