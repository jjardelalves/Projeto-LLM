from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage
import asyncio
import os
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware

#os.environ["GOOGLE_API_KEY"] = "AIzaSyAIcyrS1V_lHANkvCW1lv4yfT0mvznsis"
from dotenv import load_dotenv
load_dotenv(override=True)
load_dotenv()
#model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",max_retries=5,timeout=120)
model = ChatGroq(
    model="llama-3.3-70b-versatile", temperature=0,max_retries=5,timeout=120
)
#model = ChatOpenAI(
#    model='gpt-5-nano', max_retries=5, timeout=120
#)

client_local = MultiServerMCPClient(
     {
         "local_server": {
             "transport": "sse",
             "url":"http://localhost:8000/sse"
         }
     }
 )

async def get_tools():
    mcp_local_tools = await client_local.get_tools()
    return mcp_local_tools

# get resources

# get prompts
import asyncio

# 1. Agrupamos tudo em uma única função assíncrona
async def carregar_dados_mcp():
    # Busca as ferramentas
    tools = await client_local.get_tools()
    
    # Busca os prompts
    policy = await client_local.get_prompt("local_server", "policy_prompt")
    retriever = await client_local.get_prompt("local_server", "retriever_prompt")
    qa = await client_local.get_prompt("local_server", "qa_prompt")
    self_check = await client_local.get_prompt("local_server", "self_check_prompt")
    automation = await client_local.get_prompt("local_server", "automation_prompt")
    supervisor = await client_local.get_prompt("local_server", "supervisor_prompt")
    
    return tools, [policy, retriever, qa, self_check, automation, supervisor]

# 2. Executamos de forma síncrona para o LangGraph Studio conseguir ler
mcp_tools_list, prompts_2 = asyncio.run(carregar_dados_mcp())

agent_policy = create_agent(model=model, system_prompt=prompts_2[0][-1].content)

agent_retriver = create_agent(model=model, tools=mcp_tools_list, system_prompt=prompts_2[1][-1].content)

agent_qa = create_agent(model=model, system_prompt=prompts_2[2][-1].content)

agent_check = create_agent(model=model, system_prompt=prompts_2[3][-1].content)


@tool
async def call_policy_subagent(query: str) -> str:
  """Chama o subagente 1 que impede do usuário fazer perguntas que violam as regras impostas pelo sistema"""
  # await asyncio.sleep(3)
  response =  await agent_policy.ainvoke({"messages": [HumanMessage(content=f"Me diga se a pergunta desse usuário viola alguma das regras do sistema. {query}")]})
  return response["messages"][-1].content


@tool
async def call_retriver_subagent(query: str) -> str:
  """Chama o subagente 2 que busca os documentos mais relevantes de acordo com a query"""
  # await asyncio.sleep(3)
  response = await agent_retriver.ainvoke({"messages": [HumanMessage(content=f"Me retorne os documentos mais relevantes de acordo com essa query {query}")]})
  return response["messages"][-1].content



@tool
async def call_qa_subagent(query: str, docs: str) -> str:
  """Chama o subagente 3 que estrutura uma resposta de acordo com a pergunta e os documentos passados"""
  # await asyncio.sleep(3)
  if "NENHUM" in docs.upper() or "AVISO:" in docs.upper() or not docs.strip():
        return "Não encontrei cobertura suficiente nos materiais da disciplina para responder a esta dúvida de forma embasada."
  response = await agent_qa.ainvoke({"messages": [HumanMessage(content=f"Responda a pergunta com base nos documentos fornecidos. Pergunta: {query}. Documentos recuperados: {docs}")]})
  return response["messages"][-1].content

@tool
async def call_selfcheck_subagent(query: str, docs: str, response: str) -> str:
  """Chama o subagente 4 que valida a resposta do usuário com base em regras pré definidas e decide se é válida, necessita de re-busca ou retornar uma mensagem de pergunta inválida"""
  # await asyncio.sleep(3)
  response_agent = await agent_check.ainvoke({"messages": [HumanMessage(content=f"Valide a resposta do qa com base nas regras pré-definidas. Pergunta: {query}. Resposta: {response}. Documentos recuperados: {docs}")]})
  return response_agent["messages"][-1].content


agent = create_agent(model=model, tools=[call_retriver_subagent, call_policy_subagent, call_qa_subagent, call_selfcheck_subagent], system_prompt=prompts_2[-1][-1].content, 
                                #checkpointer=InMemorySaver(),
                               )
