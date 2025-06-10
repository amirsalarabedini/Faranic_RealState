import asyncio
import os
import sys
from typing import Literal, List, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableConfig
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage

# Add the project root to Python path to enable proper imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file in the project root
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Add the current directory to the path to allow for local imports
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.configs.llm_config import get_default_llm
from src.configs.embeddings_config import get_default_embeddings, get_current_embeddings_config
from state import AgentState
from prompts import GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
from configuration import Configuration

# --- RAG System State ---
_rag_initialized = False
_vectorstore = None
_retriever_tool = None
_response_model = None

def _initialize_rag_system(
    knowledge_file_path: str = "/Users/mac/Desktop/Faranic_RealState/data/raw/Sarmaye maskan-compressed.mdss",
    vector_store_path: str = "data/processed/faiss_index"
):
    """
    Initializes the RAG system. It loads a persistent FAISS vector store if one exists;
    otherwise, it creates a new one from the knowledge base and saves it for future use.
    """
    global _vectorstore, _retriever_tool, _response_model, _rag_initialized

    if _rag_initialized:
        return

    try:
        import faiss
    except ImportError:
        print("❌ FAISS not found. Please install it with 'pip install faiss-cpu' to enable persistence.")
        raise

    full_vector_store_path = os.path.join(project_root, vector_store_path)
    
    try:
        embeddings = get_default_embeddings()
        
        # Load the FAISS index from disk if it exists
        if os.path.exists(full_vector_store_path):
            print(f"✅ Loading existing FAISS index from {full_vector_store_path}")
            _vectorstore = FAISS.load_local(full_vector_store_path, embeddings, allow_dangerous_deserialization=True)
        # Otherwise, create it from the knowledge base
        else:
            print("💾 FAISS index not found. Creating a new one. This might take a while...")
            embeddings_config = get_current_embeddings_config()
            chunk_size = embeddings_config.get("chunk_size", 1000)
            
            full_knowledge_path = os.path.join(project_root, knowledge_file_path)
            
            content = ""
            if os.path.exists(full_knowledge_path):
                with open(full_knowledge_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"📄 Knowledge base loaded: {len(content)} characters from {full_knowledge_path}")
            else:
                print(f"⚠️  Warning: Knowledge file not found at {full_knowledge_path}. Using placeholder content.")
                content = "This is a placeholder document. The actual data file was not found."
            
            print(f"⚙️  Using chunk size: {chunk_size}")
            
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=100,
                separators=["\n\n", "\n", ". ", "؟ ", "! ", "؛ ", "، ", " ", ""]
            )
            
            docs = text_splitter.create_documents([content])
            print(f"📝 Created {len(docs)} document chunks")
            
            # Create FAISS index from documents in batches
            print("🧠 Embedding documents and creating FAISS index...")
            batch_size = 50
            
            if not docs:
                raise ValueError("No documents were created from the knowledge base. Cannot build FAISS index.")

            _vectorstore = FAISS.from_documents(documents=docs[:batch_size], embedding=embeddings)
            
            for i in range(batch_size, len(docs), batch_size):
                print(f"🔄 Processing batch {i//batch_size + 1}/{(len(docs) + batch_size - 1)//batch_size}")
                _vectorstore.add_documents(docs[i:i + batch_size])

            print(f"💾 Saving FAISS index to {full_vector_store_path}")
            os.makedirs(os.path.dirname(full_vector_store_path), exist_ok=True)
            _vectorstore.save_local(full_vector_store_path)
        
        _retriever_tool = create_retriever_tool(
            _vectorstore.as_retriever(search_kwargs={"k": 5}),
            "retrieve_real_estate_knowledge",
            "Search and return information from the Persian real estate book."
        )
        
        _response_model = get_default_llm()
        _rag_initialized = True
        print("✅ RAG system initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        raise e

async def generate_query_or_respond(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Asynchronously decides whether to retrieve from knowledge base or respond directly."""
    try:
        formatted_messages = [HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) for msg in messages]
        response = await _response_model.bind_tools([_retriever_tool]).ainvoke(formatted_messages)
        return {"content": response.content, "tool_calls": getattr(response, 'tool_calls', [])}
    except Exception as e:
        print(f"❌ Error in generate_query_or_respond: {e}")
        return {"content": f"Error processing query: {e}", "tool_calls": []}

async def retrieve_knowledge(query: str) -> str:
    """Asynchronously retrieves relevant knowledge from the knowledge base."""
    try:
        return await _retriever_tool.ainvoke({"query": query})
    except Exception as e:
        print(f"❌ Error retrieving knowledge: {e}")
        return f"Error retrieving knowledge: {e}"

async def grade_documents(question: str, retrieved_content: str) -> str:
    """Asynchronously grades the relevance of retrieved documents."""
    try:
        prompt = GRADE_PROMPT.format(question=question, document=retrieved_content)
        response = await _response_model.ainvoke([HumanMessage(content=prompt)])
        return "yes" if "yes" in response.content.lower() else "no"
    except Exception as e:
        print(f"❌ Error grading documents: {e}")
        return "no"

async def rewrite_question(original_question: str) -> str:
    """Asynchronously rewrites the question for better retrieval."""
    try:
        prompt = REWRITE_PROMPT.format(question=original_question)
        response = await _response_model.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"❌ Error rewriting question: {e}")
        return original_question

async def generate_answer(question: str, context: str) -> str:
    """Asynchronously generates a final answer based on question and retrieved context."""
    try:
        prompt = GENERATE_PROMPT.format(question=question, context=context)
        response = await _response_model.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        print(f"❌ Error generating answer: {e}")
        return f"Error generating answer: {e}"


# --- Graph Nodes ---
async def start_agent(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Initializes the agent's state at the beginning of a run."""
    _initialize_rag_system()
    configurable = Configuration.from_runnable_config(config)
    return {
        "messages": [{"role": "user", "content": state["query"]}],
        "iteration": 0,
        "max_iterations": configurable.max_iterations,
    }

async def decide_to_retrieve(state: AgentState) -> Dict[str, Any]:
    """Calls the LLM to decide whether to use the retriever tool or respond directly."""
    print("---DECIDING TO RETRIEVE---")
    result = await generate_query_or_respond(state["messages"])
    
    if not result["tool_calls"]:
        return {"answer": result["content"]}
    else:
        query = result["tool_calls"][0]["args"]["query"]
        return {"rewritten_query": query}

async def retrieve_knowledge_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves knowledge from the vectorstore using the generated query."""
    print("---RETRIEVING KNOWLEDGE---")
    documents = await retrieve_knowledge(state["rewritten_query"])
    return {"documents": documents, "iteration": state["iteration"] + 1}

async def grade_documents_node(state: AgentState) -> Dict[str, str]:
    """Grades the relevance of the retrieved documents against the original query."""
    print("---GRADING DOCUMENTS---")
    grade = await grade_documents(state["query"], state["documents"])
    return {"grade": grade}

async def generate_answer_node(state: AgentState) -> Dict[str, str]:
    """Generates a final answer using the relevant retrieved documents."""
    print("---GENERATING ANSWER---")
    answer = await generate_answer(state["query"], state["documents"])
    return {"answer": answer}

async def rewrite_question_node(state: AgentState) -> Dict[str, List]:
    """Rewrites the original question to improve retrieval results."""
    print("---REWRITING QUESTION---")
    rewritten_query = await rewrite_question(state["query"])
    return {"messages": [{"role": "user", "content": rewritten_query}]}

async def end_agent(state: AgentState) -> Dict[str, str]:
    """A final node to handle cases where the max iterations are reached."""
    print("---MAX ITERATIONS REACHED, ENDING---")
    return {"answer": "Unable to find relevant information after multiple attempts."}


# --- Conditional Edges ---
def should_retrieve(state: AgentState) -> Literal["retrieve_knowledge", "end_with_direct_answer"]:
    """Determines the next step after the initial decision node."""
    if "answer" in state and state["answer"]:
        return "end_with_direct_answer" 
    return "retrieve_knowledge"

def grade_and_decide(state: AgentState) -> Literal["generate_answer", "rewrite_question", "end_agent"]:
    """Decides the next step based on the document grade and iteration count."""
    if state["grade"] == "yes":
        return "generate_answer"
    elif state["iteration"] < state["max_iterations"]:
        return "rewrite_question"
    else:
        return "end_agent"


# --- Graph Definition ---
builder = StateGraph(AgentState)

builder.add_node("start_agent", start_agent)
builder.add_node("decide_to_retrieve", decide_to_retrieve)
builder.add_node("retrieve_knowledge", retrieve_knowledge_node)
builder.add_node("grade_documents", grade_documents_node)
builder.add_node("generate_answer", generate_answer_node)
builder.add_node("rewrite_question", rewrite_question_node)
builder.add_node("end_agent", end_agent)

builder.add_edge(START, "start_agent")
builder.add_edge("start_agent", "decide_to_retrieve")

builder.add_conditional_edges(
    "decide_to_retrieve",
    should_retrieve,
    {
        "retrieve_knowledge": "retrieve_knowledge",
        "end_with_direct_answer": END,
    }
)
builder.add_edge("retrieve_knowledge", "grade_documents")
builder.add_conditional_edges(
    "grade_documents",
    grade_and_decide,
    {
        "generate_answer": "generate_answer",
        "rewrite_question": "rewrite_question",
        "end_agent": "end_agent"
    }
)
builder.add_edge("rewrite_question", "decide_to_retrieve")
builder.add_edge("generate_answer", END)
builder.add_edge("end_agent", END)

_graph = builder.compile()

def get_knowledge_agent():
    """Returns the compiled knowledge base agent."""
    _initialize_rag_system()
    return _graph

async def test_graph():
    """Tests the graph with a sample input query."""
    app = get_knowledge_agent()
    config = Configuration()
    
    query = "What were the key factors affecting the housing market in Iran"
    
    async for event in app.astream_events(
        {"query": query}, 
        config={"configurable": config.to_dict()},
        version="v1"
    ):
        kind = event["event"]
        if kind == "on_chain_end":
            if event["name"] == "start_agent":
                print(f"---AGENT STARTED---")
                print(f"Initial State: {event['data'].get('output')}")
        if kind == "on_chain_stream":
            if event["name"] == "generate_answer":
                print(f"\n---FINAL ANSWER---")
                print(event["data"]["chunk"].get("answer"))

if __name__ == "__main__":
    asyncio.run(test_graph()) 