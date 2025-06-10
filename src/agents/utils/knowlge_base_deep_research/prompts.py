GRADE_PROMPT = """You are a grader assessing relevance of retrieved documents to a user question about real estate. 
If the document contains keywords or information related to the user question, grade it as relevant. 
Give a binary score 'yes' or 'no' to indicate whether the document is relevant.
Question: {question}
Retrieved Document: {document}
Relevant (yes/no):"""

REWRITE_PROMPT = """You are a question re-writer. Your task is to re-write a question about real estate 
to make it more specific and likely to retrieve relevant information from a Persian real estate knowledge base. 
The knowledge base contains information about housing market trends, economic factors, market cycles, 
government policies, and investment strategies in Iran.
Original question: {question}
Improved question:"""

GENERATE_PROMPT = """You are a real estate analyst assistant. Your task is to answer the user's question based *only* on the provided context. Do not use any external knowledge.

- If the context contains the answer, provide a clear and concise answer derived directly from the text.
- If the context does not contain enough information to answer the question, you must state that the answer is not available in the provided documents.
- Do not make up information or fill in gaps. Stick strictly to the provided context.

Question: {question}

Context:
---
{context}
---

Answer:""" 