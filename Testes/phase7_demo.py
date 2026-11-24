"""Safe demonstration: uses a fake model callback, not a real API."""
from kenzie_cognition.pipeline import CognitivePipeline
from kenzie_cognition.integration import KenzieCognitiveAdapter

adapter = KenzieCognitiveAdapter(CognitivePipeline())
def fake_model(messages):
    print("\n--- Messages sent to host model ---")
    for message in messages:
        print(message["role"], ":", message["content"][:500])
    return "[Resposta simulada: conecte aqui a função de chat já existente da Kenzie.]"

answer, turn = adapter.run(
    "Explique como funciona uma API REST", fake_model,
    history=[{"role": "user", "content": "Estou estudando programação"}],
    system_prompt="Você é Kenzie, assistente de programação."
)
print("\nResposta:", answer)
print("Modo sugerido:", turn.analysis.response_mode)
