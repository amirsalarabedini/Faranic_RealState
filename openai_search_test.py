from src.configs.llm_config import get_llm

llm = get_llm(model="gpt-4o-mini")

print(llm.invoke("Hello, world!"))