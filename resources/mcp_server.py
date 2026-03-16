from dotenv import load_dotenv
from langchain.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()


from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
from requests import get
import os


mcp = FastMCP("mcp_server")

DIRETORIO_BANCO = os.path.abspath('../db_chroma')
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

vector_store = Chroma(
    persist_directory=DIRETORIO_BANCO,
    embedding_function=embeddings,
    collection_name="concorrencia_db"
)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

@mcp.tool("search_for_information_on_indexed_documents")
def search_for_information_on_indexed_documents(query: str) -> str:
    """Busca informações nos documentos PDF indexados para responder ao aluno."""
    try:
        # Tenta recuperar os documentos
        documentos_encontrados = retriever.invoke(query)
        
        if not documentos_encontrados:
            return "AVISO: Nenhum trecho relevante foi encontrado nos livros sobre este assunto."

        resultados = []
        for doc in documentos_encontrados:
            pagina = doc.metadata.get('page', 'Desconhecida')
            origem = doc.metadata.get('source', 'Desconhecida')
            resultados.append(f"FONTE: {origem} (Pág {pagina})\nCONTEÚDO: {doc.page_content}\n---")

        return "\n\n".join(resultados)
    except Exception as e:
        return f"Erro ao acessar o banco de dados: {str(e)}"




# Prompt template
@mcp.prompt()
def prompt():
    """Prompt de um agente recuperador de documentos"""
    return """
    Você é o Agente Recuperador de um assistente educacional de Programação Concorrente.
    Sua única responsabilidade é buscar trechos relevantes nos documentos indexados da disciplina.

    ## Comportamento esperado

    Dado uma query do aluno, você deve:
    1. Usar a ferramenta `search_for_information_on_indexed_documents` para buscar passagens relevantes.
    2. Retornar os trechos encontrados com suas respectivas fontes e páginas, SEM interpretar ou responder.
    3. Se nenhum trecho relevante for encontrado, retornar explicitamente: "NENHUMA_EVIDENCIA_ENCONTRADA".

    ## Formato de saída

    Retorne os trechos no seguinte formato:

    [TRECHO 1]
    Fonte: <nome do documento> | Página: <número>
    Conteúdo: <texto do trecho>

    [TRECHO 2]
    ...

    ## Restrições
    - NÃO responda à pergunta do aluno.
    - NÃO adicione interpretações, resumos ou opiniões.
    - NÃO invente trechos. Retorne APENAS o que foi encontrado nas ferramentas.
    - Se a busca retornar resultados irrelevantes, informe: "TRECHOS_IRRELEVANTES".
    """

if __name__ == "__main__":
    mcp.run(transport="sse")