from dotenv import load_dotenv
from langchain.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()


from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict, Any
from requests import get


mcp = FastMCP("mcp_server")

tavily_client = TavilyClient()

DIRETORIO_BANCO = '../db_chroma'

def configurar_retriever(diretorio_banco=DIRETORIO_BANCO):
    #print("Carregando os embeddings e o banco de dados do disco...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

    vector_store = Chroma(
        persist_directory=diretorio_banco,
        embedding_function=embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    return retriever

@mcp.tool("search_for_information_on_indexed_documents")
def search_for_information_on_indexed_documents(query:str):
    """Search for information within the indexed PDF documents to answer user queries."""
    retriever = configurar_retriever()
    documentos_encontrados = retriever.invoke(query)

    if not documentos_encontrados:
        print("Nenhuma informação relevante encontrada.")
        return []

    resultados = []

    for i, doc in enumerate(documentos_encontrados, 1):
        conteudo = doc.page_content
        metadados = doc.metadata

        pagina = metadados.get('page', 'Desconhecida')
        origem = metadados.get('source', 'Desconhecida')

        formato = f"FONTE: {origem} (Página {pagina})\nCONTEÚDO: {conteudo}\n---"
        resultados.append(formato)


        #print(f"--- Trecho {i} ---")
        #print(f" Página: {pagina} |  Documento: {origem}")
        #print(f" Texto: {conteudo[:300]}...\n")

    return "\n\n".join(resultados)


# Resources - provide access to langchain-ai repo files
@mcp.resource("github://langchain-ai/langchain-mcp-adapters/blob/main/README.md")
def github_file():
    """
    Resource for accessing langchain-ai/langchain-mcp-adapters/README.md file

    """
    url = f"https://raw.githubusercontent.com/langchain-ai/langchain-mcp-adapters/blob/main/README.md"
    try:
        resp = get(url)
        return resp.text
    except Exception as e:
        return f"Error: {str(e)}"


# Prompt template
@mcp.prompt()
def prompt():
    """Analyze data from a langchain-ai repo file with comprehensive insights"""
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