from src.configs.llm_config import get_llm

llm = get_llm(model="gpt-4o-mini", provider="openai")

print(llm.invoke("Hello, world!"))

print("--------------------------------")


from src.configs.embeddings_config import get_embeddings
embeddings = get_embeddings(model="text-embedding-3-small", provider="openai")

# Fix the error: 'SimpleOpenAIEmbeddings' object has no attribute 'invoke'
# Use embed() method instead of invoke()
print(embeddings.embed_query("Hello, world!"))
print("--------------------------------")