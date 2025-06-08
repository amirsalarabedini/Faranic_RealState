from langsmith import traceable
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import Dict, Any, List
import os
import json
from datetime import datetime
from src.config import get_default_embeddings, get_default_llm, get_current_embeddings_config

class KnowledgeRetriever:
    """Agentic RAG system for accessing the real estate knowledge base"""
    
    def __init__(self, knowledge_file_path: str = "data/raw/processed/ocr_results_combined.md"):
        self.knowledge_file_path = knowledge_file_path
        self.vectorstore = None
        self.retriever_tool = None
        self.response_model = None
        self._initialize_rag_system()
    
    def _initialize_rag_system(self):
        """Initialize the RAG system with vectorstore and retriever tool"""
        try:
            # Get embeddings configuration
            embeddings_config = get_current_embeddings_config()
            chunk_size = embeddings_config.get("chunk_size", 1000)
            
            # Read the knowledge base
            with open(self.knowledge_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 Knowledge base loaded: {len(content)} characters")
            print(f"⚙️  Using chunk size: {chunk_size}")
            
            # Split the content into chunks using config chunk size
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=chunk_size,
                chunk_overlap=100,
                separators=[
                    "\n\n",        # Double newline (paragraphs)
                    "\n",          # Single newline (lines)
                    ". ",          # Sentence endings
                    "؟ ",          # Persian question mark
                    "! ",          # Exclamation mark
                    "؛ ",          # Persian semicolon
                    "، ",          # Persian comma
                    " ",           # Spaces (word boundaries)
                    "",            # Character level (last resort)
                ]
            )
            
            # Create documents from the content
            docs = text_splitter.create_documents([content])
            print(f"📝 Created {len(docs)} document chunks")
            
            # Process documents in smaller batches to avoid API limits
            batch_size = 50 # Process 50 documents at a time to avoid token limits
            all_docs = []
            vectorstore_initialized = False
            
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                print(f"🔄 Processing batch {i//batch_size + 1}/{(len(docs) + batch_size - 1)//batch_size} ({len(batch)} docs)")
                
                # Create or add to vectorstore
                if not vectorstore_initialized:
                    # First successful batch - create new vectorstore
                    self.vectorstore = InMemoryVectorStore.from_documents(
                        documents=batch, 
                        embedding=get_default_embeddings()
                    )
                    vectorstore_initialized = True
                    print(f"✅ Vectorstore initialized with batch {i//batch_size + 1}")
                else:
                    # Subsequent batches - add to existing vectorstore
                    self.vectorstore.add_documents(batch)
                    print(f"✅ Added batch {i//batch_size + 1} to vectorstore")
                
                all_docs.extend(batch)
            
            # Check if vectorstore was successfully initialized
            if not vectorstore_initialized or self.vectorstore is None:
                raise Exception("Failed to initialize vectorstore - all batches failed. Please check your API connectivity and credentials.")
            
            print(f"✅ Successfully processed {len(all_docs)} documents out of {len(docs)} total")
            
            # Create retriever tool
            self.retriever_tool = create_retriever_tool(
                self.vectorstore.as_retriever(search_kwargs={"k": 5}),
                "retrieve_real_estate_knowledge",
                "Search and return information from the Persian real estate book about housing market trends, economic factors, market cycles, and investment strategies."
            )
            
            # Initialize response model
            self.response_model = get_default_llm()
            
            print("✅ Knowledge retriever initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing knowledge retriever: {e}")
            raise e
    
    @traceable
    def generate_query_or_respond(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Decide whether to retrieve from knowledge base or respond directly"""
        try:
            # Convert messages to proper format
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    formatted_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_messages.append(AIMessage(content=msg["content"]))
            
            # Call model with retriever tool
            response = self.response_model.bind_tools([self.retriever_tool]).invoke(formatted_messages)
            
            return {
                "content": response.content,
                "tool_calls": response.tool_calls if hasattr(response, 'tool_calls') else []
            }
            
        except Exception as e:
            print(f"❌ Error in generate_query_or_respond: {e}")
            return {"content": f"Error processing query: {e}", "tool_calls": []}
    
    @traceable
    def retrieve_knowledge(self, query: str) -> str:
        """Retrieve relevant knowledge from the knowledge base"""
        try:
            result = self.retriever_tool.invoke({"query": query})
            return result
        except Exception as e:
            print(f"❌ Error retrieving knowledge: {e}")
            return f"Error retrieving knowledge: {e}"
    
    @traceable
    def grade_documents(self, question: str, retrieved_content: str) -> str:
        """Grade the relevance of retrieved documents"""
        GRADE_PROMPT = (
            "You are a grader assessing relevance of retrieved documents to a user question about real estate. "
            "If the document contains keywords or information related to the user question, grade it as relevant. "
            "Give a binary score 'yes' or 'no' to indicate whether the document is relevant.\n"
            "Question: {question}\n"
            "Retrieved Document: {document}\n"
            "Relevant (yes/no):"
        )
        
        try:
            prompt = GRADE_PROMPT.format(question=question, document=retrieved_content)
            response = self.response_model.invoke([{"role": "user", "content": prompt}])
            
            return "yes" if "yes" in response.content.lower() else "no"
            
        except Exception as e:
            print(f"❌ Error grading documents: {e}")
            return "no"
    
    @traceable
    def rewrite_question(self, original_question: str) -> str:
        """Rewrite the question for better retrieval"""
        REWRITE_PROMPT = (
            "You are a question re-writer. Your task is to re-write a question about real estate "
            "to make it more specific and likely to retrieve relevant information from a Persian real estate knowledge base. "
            "The knowledge base contains information about housing market trends, economic factors, market cycles, "
            "government policies, and investment strategies in Iran.\n"
            "Original question: {question}\n"
            "Improved question:"
        )
        
        try:
            prompt = REWRITE_PROMPT.format(question=original_question)
            response = self.response_model.invoke([{"role": "user", "content": prompt}])
            return response.content.strip()
            
        except Exception as e:
            print(f"❌ Error rewriting question: {e}")
            return original_question
    
    @traceable
    def generate_answer(self, question: str, context: str) -> str:
        """Generate final answer based on question and retrieved context"""
        GENERATE_PROMPT = (
            "You are an expert real estate analyst assistant. Use the following retrieved context "
            "from a Persian real estate book to answer the question. The context may contain information "
            "about housing market trends, economic factors, market cycles, and investment strategies in Iran. "
            "If you don't know the answer based on the context, say so. "
            "Provide a comprehensive but concise answer.\n"
            "Question: {question}\n"
            "Context: {context}\n"
            "Answer:"
        )
        
        try:
            prompt = GENERATE_PROMPT.format(question=question, context=context)
            response = self.response_model.invoke([{"role": "user", "content": prompt}])
            return response.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return f"Error generating answer: {e}"
    
    @traceable
    def process_query(self, query: str, max_iterations: int = 3) -> Dict[str, Any]:
        """Process a query using the agentic RAG system"""
        print(f"🔍 Processing query: {query}")
        
        messages = [{"role": "user", "content": query}]
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"🔄 Iteration {iteration}")
            
            # Step 1: Decide whether to retrieve or respond
            decision = self.generate_query_or_respond(messages)
            
            # If no tool calls, return direct response
            if not decision["tool_calls"]:
                return {
                    "answer": decision["content"],
                    "source": "direct_response",
                    "iterations": iteration
                }
            
            # Step 2: Retrieve knowledge
            tool_call = decision["tool_calls"][0]
            if tool_call["name"] == "retrieve_real_estate_knowledge":
                retrieved_content = self.retrieve_knowledge(tool_call["args"]["query"])
                
                # Step 3: Grade documents
                relevance = self.grade_documents(query, retrieved_content)
                
                if relevance == "yes":
                    # Step 4: Generate final answer
                    answer = self.generate_answer(query, retrieved_content)
                    return {
                        "answer": answer,
                        "source": "knowledge_base",
                        "retrieved_content": retrieved_content,
                        "iterations": iteration
                    }
                else:
                    # Step 5: Rewrite question and try again
                    rewritten_query = self.rewrite_question(query)
                    print(f"🔄 Rewritten query: {rewritten_query}")
                    messages = [{"role": "user", "content": rewritten_query}]
                    continue
        
        # If max iterations reached, return what we have
        return {
            "answer": "Unable to find relevant information after multiple attempts.",
            "source": "max_iterations_reached",
            "iterations": iteration
        }

# Global instance
_knowledge_retriever = None

def get_knowledge_retriever() -> KnowledgeRetriever:
    """Get or create the global knowledge retriever instance"""
    global _knowledge_retriever
    if _knowledge_retriever is None:
        _knowledge_retriever = KnowledgeRetriever()
    return _knowledge_retriever 