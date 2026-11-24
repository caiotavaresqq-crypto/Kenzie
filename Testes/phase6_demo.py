from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.knowledge_base import KnowledgeBase

history = [
    {"role": "user", "content": "Estou criando um aplicativo em Python."},
    {"role": "assistant", "content": "Certo. Qual parte você quer desenvolver?"},
]
pipeline = CognitivePipeline(knowledge_base=KnowledgeBase())
result = pipeline.analyze("Planeje como criar uma API para esse aplicativo.", history)
print("MODO:", result.response_mode)
print("INTENÇÃO:", result.comprehension["intent"])
print("PLANO:")
for action in result.next_actions:
    print("-", action)
print("RESULTADO ESTRUTURADO:")
print(result.to_dict())
