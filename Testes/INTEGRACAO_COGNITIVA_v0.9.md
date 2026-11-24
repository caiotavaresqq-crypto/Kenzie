# Kenzie 0.9 — Evolução da integração cognitiva

A versão 0.9 mantém a arquitetura cognitiva transferida da 0.7/0.8, mas altera a chamada de geração: `Kenzie.py` prepara a mensagem pelo `KenzieOrchestrator` e envia ao `LocalInferenceEngine`, que usa apenas o endpoint local Ollama por padrão. A ponte cognitiva não realiza chamadas a serviços de IA.

## Fluxo atualizado
1. Mensagem chega à interface/entrada e passa pelos comandos locais e memória existentes.
2. `montar_mensagens_ia()` registra a mensagem no histórico e recupera fatos do SQLite, quando a recuperação está habilitada.
3. `KenzieOrchestrator.prepare_turn()` monta histórico/contexto e chama o `cognitive_bridge`, quando habilitado.
4. O Cognitive Core analisa intenção, contexto, ambiguidades, estrutura de problema e candidatos de conhecimento. Sua análise é incluída no prompt como contexto advisory.
5. `LocalInferenceEngine` consulta a instância Ollama em `127.0.0.1` e usa o modelo configurado.
6. Tool calls são validadas e executadas pelo Action Engine existente. A síntese dos resultados é feita novamente pelo modelo local.
7. Resposta é armazenada no histórico local e entregue à interface/voz.

## OpenRouter e APIs
A versão 0.9 remove o OpenRouter/OpenAI do fluxo principal. Os clientes antigos são mantidos como variáveis nulas de compatibilidade. Não existe fallback automático remoto. A configuração legada no `.env` não é consumida pelo motor local.

## Componentes
- `local_inference_engine.py`: backend de geração e configuração, status do Ollama, chamada de inferência e helper explícito de pull de modelo.
- `orchestrator.py`: coordena histórico, memória/contexto e Cognitive Core.
- `research_engine.py`: pesquisa web independente, sem chave de API, leitura conservadora com checagem de robots.
- `action_engine_tools.py`: adiciona `research_web` ao catálogo de ferramentas, preservando ações existentes.
- `Kenzie.py`: fluxo de conversa, aviso vocal, geração local, execução de ferramentas e síntese local.
- `tests/test_local_engine.py` e `tests/test_research_engine.py`: testes isolados/mocks.

## Reversibilidade e toggles
- `KENZIE_LOCAL_ENABLED=0`: bloqueia inferência local; o programa informa indisponibilidade sem fallback externo.
- `KENZIE_COGNITION_ENABLED=0`: desativa análise cognitiva.
- `KENZIE_MEMORY_RETRIEVAL_ENABLED=0`: desativa injeção de fatos da memória no prompt, sem apagar banco nem parar o histórico.
- `KENZIE_RESEARCH_ENABLED=0`: desativa pesquisa web.
- `KENZIE_THINKING_VOICE=0`: desativa frase vocal durante processamento.
