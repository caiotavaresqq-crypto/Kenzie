from kenzie_cognition import understand_message

history = [
    {"role": "assistant", "content": "O módulo de memória usa SQLite e mantém origem e confiança."},
    {"role": "user", "content": "Quero melhorar o módulo de memória."},
]
result = understand_message("Corrige isso e explica o que mudou", history)
print("Intent:", result.intent)
print("Mode:", result.suggested_response_mode)
print("References:", result.references)
print("Ambiguity:", result.ambiguity)
print("Context preview:\n", result.context["summary"])
