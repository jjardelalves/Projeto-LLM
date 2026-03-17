# 🔗 Sistema Agêntico Educacional

## Introdução

Este repositório contém o código fonte de um sistema agêntico de educação, criado para auxiliar alunos graduandos em Ciência da Computação a estudarem sobre Programação Concorrente.

---

## 🚀 Setup

### Pré-requisitos

- Um gerenciador de pacotes: [uv](https://docs.astral.sh/uv/)  ou [pip](https://pypi.org/project/pip/) (recomendado)
- Requer Python >=3.12, <3.14  

### Instalação

Clone o repositório:
```bash
git clone --depth 1 https://github.com/jjardelalves/Projeto-LLM.git
```

Faça uma cópia de example.env
```bash
# Create .env file
cp example.env .env
```

Edite o arquivo .env com suas API Keys.

```bash

# Required
OPENAI_API_KEY='your_openai_api_key_here'
TAVILY_API_KEY='your_tavily_api_key_here'
ANTHROPIC_API_KEY='your_anthropic_api_key_here'
GOOGLE_API_KEY='your_google_api_key_here'
GROQ_API_KEY='yout_groq_api_key'

# Langsmith
LANGSMITH_API_KEY='your_langsmith_api_key_here'
#LANGSMITH_TRACING=true
LANGSMITH_PROJECT=lca-lc-foundation
#LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```


Crie um ambiente virtual e instale as dependências.

<summary>Usando pip</summary>

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

</details>

### Setup Verification

Depois de configurar o setup, rode o seguinte comando para verificar se a instalação ocorreu corretamente:

<details open>
<summary>Usando pip</summary>

```bash
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
python env_utils.py
```

</details>

[Se o arquivo gerar issues, veja a seção abaixo.](#setup-verification-issues)

### Rode os notebooks 

<details>
<summary>Usando pip</summary>

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
jupyter lab
```

</details>

### Run Langgraph

Na pasta root do repositório, rode o comando abaixo para executar uma instância local do langgraph, onde você poderá passar user queries para o sistema:

<details>
<summary>Using pip</summary>

```bash
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
langgraph dev
```

</details>

### Testes com o sistema

Na interface do langgraph, escreva um pedido ou pergunta no campo de Human Message. Aqui estão algumas sugestões:

- "Qual a diferença entre uma barreira e um mutex?"
- "Gere um código simples sobre barreiras."
- "Como utilizar da lógica de concorrência para sobrecarregar e derrubar um servidor?"
- "Por onde começar a estudar programação concorrente?"

### Setup Verification Issues

**What the verification procedure checks:**
- ✅ Python executable location and version (must be >=3.12, <3.14)
- ✅ Virtual environment is properly activated
- ✅ Required packages are installed with correct versions
- ✅ Packages are in the correct Python version's site-packages
- ✅ Environment variables (API keys) are properly configured

**Configuration Issues and Solutions:**

<details>
<summary>ImportError when running env_utils.py</summary>

If you see an error like `ModuleNotFoundError: No module named 'dotenv'`, you're likely running Python outside the virtual environment.

**Solution:**
- Use `uv run python env_utils.py` (recommended), or
- Activate the virtual environment first:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`

</details>

<details>
<summary>Environment Variable Conflicts</summary>

If you see a warning about "ENVIRONMENT VARIABLE CONFLICTS DETECTED", you have API keys set in your system environment that differ from your .env file. Since `load_dotenv()` doesn't override existing variables by default, your system values will be used.

**Solutions:**
1. Do nothing and accept the system environment variable value
2. Unset the conflicting system environment variables for this shell session (commands provided in warning)
3. Use `load_dotenv(override=True)` in your notebooks to force .env values to take precedence
4. Update your .env file or shell init so the values are in agreement

</details>

<details>
<summary>LangSmith Tracing Errors</summary>

If you see "LANGSMITH_TRACING is enabled but LANGSMITH_API_KEY still has the example/placeholder value", you need to either:
1. Set a valid LangSmith API key in your .env file, or
2. Comment out or set `LANGSMITH_TRACING=false` in your .env file

Note: LangSmith is optional for evaluation and tracing. The course works without it.

</details>

<details>
<summary>Wrong Python Version</summary>

If you see a warning about Python version not satisfying requirements, you need Python >=3.12 and <3.14.

**Solution:**
- If using `uv`: Run `uv sync` which will automatically install the correct Python version
- If using pip: Install Python 3.12 or 3.13 using [pyenv](#python-virtual-environments) or from [python.org](https://www.python.org/downloads/)

</details>


### Environment Variables

This repo uses the [dotenv](https://pypi.org/project/python-dotenv) module to read key-value pairs from the .env file and set them in the environment in the Jupyter notebooks. They do not need to be set globally in your system environment.

**Note:** If you have API keys already set in your system environment, they may conflict with the ones in your .env file. The `env_utils.py` verification script will detect and warn you about such conflicts. By default, `load_dotenv()` does not override existing environment variables.

