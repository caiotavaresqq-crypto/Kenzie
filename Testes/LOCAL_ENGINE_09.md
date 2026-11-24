# Kenzie 0.9 — Local Intelligence Engine

## O que muda
- Inferência local via Ollama e endpoint OpenAI-compatible em `127.0.0.1:11434/v1`.
- Modelo padrão configurável: `qwen2.5:1.5b`.
- OpenRouter/OpenAI não são inicializados no fluxo de conversa e não há fallback remoto.
- Cognitive Core, memória SQLite, Action Engine, interface e voz são preservados.
- A pesquisa externa é um recurso separado (`research_web`), não o gerador de respostas. Ela tenta usar DuckDuckGo HTML, limita páginas, usa User-Agent identificável e verifica `robots.txt` antes de ler páginas. Se não conseguir verificar robots, ignora a página. Pesquisa exige internet; inferência local não.

## Instalação
1. Instale Python e as dependências do `requirements.txt`.
2. Instale Ollama pelo instalador oficial: https://ollama.com/download
3. Abra um terminal na pasta do projeto e execute `ollama pull qwen2.5:1.5b` (ou use `INSTALAR_KENZIE_09.bat`).
4. Copie `.env.example` para `.env` e ajuste as opções, se desejar.
5. Inicie Ollama (normalmente o aplicativo inicia o serviço) e a Kenzie.
6. Se estiver sem internet após baixar o modelo, conversas continuam locais. Pesquisa externa fica indisponível.

## Configuração
| Variável | Padrão | Descrição |
|---|---|---|
| `KENZIE_LOCAL_ENABLED` | `1` | Ativa a inferência local. Se `0`, conversa IA fica indisponível, sem API externa. |
| `KENZIE_LOCAL_BASE_URL` | `http://127.0.0.1:11434/v1` | Endpoint local Ollama. |
| `KENZIE_LOCAL_MODEL` | `qwen2.5:1.5b` | Nome do modelo local instalado. |
| `KENZIE_LOCAL_TEMPERATURE` | `0.7` | Temperatura. |
| `KENZIE_LOCAL_MAX_TOKENS` | `900` | Limite de saída. |
| `KENZIE_LOCAL_TIMEOUT` | `90` | Timeout em segundos. |
| `KENZIE_COGNITION_ENABLED` | `1` | Desativa/ativa o Cognitive Core. |
| `KENZIE_MEMORY_RETRIEVAL_ENABLED` | `1` | Desativa/ativa recuperação de fatos da memória no prompt (registro/histórico continuam preservados). |
| `KENZIE_RESEARCH_ENABLED` | `0` | Pesquisa externa, opt-in. Defina `1` para autorizar. |
| `KENZIE_BROWSER_ACTIONS_ENABLED` | `0` | Autoriza abrir sites/pesquisa no navegador via Action Engine. Defina `1` para autorizar. |
| `KENZIE_THINKING_VOICE` | `1` | Aviso vocal de processamento. |

## Segurança e privacidade
- Nenhuma mensagem, histórico ou memória é enviada a OpenRouter/OpenAI.
- Pesquisa recebe somente o texto da consulta que o modelo/usuário solicitar; não envia conversa ou memória. Sites pesquisados podem receber requisições HTTP de leitura.
- O motor local verifica disponibilidade antes de gerar. Se falhar, informa o problema; não troca silenciosamente para serviço externo.
- A pesquisa não tenta contornar paywalls, login ou restrições de robots.txt. O acesso pode falhar e a Kenzie deve indicar isso.
- A pesquisa retorna snippets/extratos para o modelo. As fontes devem ser verificadas, e divergências ou ausência de evidência não devem ser tratadas como certeza.

## Diagnóstico
- Ollama: `ollama list`, `ollama ps` e `ollama --version`.
- Modelo: `ollama show qwen2.5:1.5b`.
- Teste rápido: `ollama run qwen2.5:1.5b "Responda em uma frase: o que é a água?"`.
- Inferência: veja `[IA LOCAL]` no terminal.
- Cognição: veja `[Cognition]`.
- Para desativar cognição: `KENZIE_COGNITION_ENABLED=0`.
- Para desativar aviso vocal: `KENZIE_THINKING_VOICE=0`.
- Pesquisa externa fica desligada por padrão; para habilitar: `KENZIE_RESEARCH_ENABLED=1`. Para ações de navegador, habilite `KENZIE_BROWSER_ACTIONS_ENABLED=1`.
- API externa: clientes remotos não são inicializados na versão 0.9.

## Modelo inicial verificado
O registro oficial do Ollama lista `qwen2.5:1.5b` com tamanho de download aproximado de 986 MB e a família Qwen2.5 aparece como compatível com ferramentas. Isso confirma disponibilidade no catálogo e suporte de ferramenta em nível de família, não desempenho no computador específico. Referências: https://ollama.com/library/qwen2.5 e https://ollama.com/blog/tool-support

## Limitações verificadas nesta entrega
O hardware real e a instalação local do Ollama não estavam disponíveis durante o desenvolvimento. Portanto, inferência real, latência, consumo de RAM/VRAM, funcionamento com a internet fisicamente desligada e compatibilidade de tool-calling com o modelo selecionado permanecem testes pendentes no computador do usuário. O Qwen 2.5 1.5B é uma opção inicial de baixa escala, não uma garantia de qualidade ou desempenho.
