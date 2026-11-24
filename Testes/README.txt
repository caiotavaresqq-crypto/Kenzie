KENZIE 0.9 — LOCAL INTELLIGENCE ENGINE
=======================================

STATUS
- Conversational generation now defaults to the local Ollama engine.
- OpenRouter/OpenAI clients are not initialized or called by the main conversation flow.
- No remote fallback exists. When local inference is unavailable, Kenzie reports that clearly.
- Cognitive Core, SQLite memory, Learning Engine, Action Engine, interface, and voice are retained.
- Research is separate from language generation and can access web sources only when explicitly selected by the assistant/tool call and when internet is available.

INSTALL
1. Install Python 3.10+ (recommended) and dependencies:
   python -m pip install -r requirements.txt
2. Install Ollama: https://ollama.com/download
3. Download the default model:
   ollama pull qwen2.5:1.5b
   Or run INSTALAR_KENZIE_09.bat from Windows.
4. Copy .env.example to .env and adjust settings if needed.
5. Start Ollama, then run INICIAR_KENZIE.bat.

LOCAL MODEL SETTINGS (.env)
KENZIE_LOCAL_ENABLED=1
KENZIE_LOCAL_BASE_URL=http://127.0.0.1:11434/v1
KENZIE_LOCAL_MODEL=qwen2.5:1.5b
KENZIE_LOCAL_TEMPERATURE=0.7
KENZIE_LOCAL_MAX_TOKENS=900
KENZIE_LOCAL_TIMEOUT=90

COMPONENT SWITCHES
KENZIE_COGNITION_ENABLED=1   # Cognitive Core
KENZIE_RESEARCH_ENABLED=0    # Web research tool (opt-in)
KENZIE_BROWSER_ACTIONS_ENABLED=0 # Browser launches/search (opt-in)
KENZIE_THINKING_VOICE=1     # Processing voice phrase
Set a component to 1 to enable it when default is 0, or 0 to disable it. Web research and browser actions are opt-in. Local inference disabled means Kenzie will not call a remote provider as fallback.

RESEARCH ENGINE
The research_web tool is disabled by default (`KENZIE_RESEARCH_ENABLED=0`). After explicitly enabling it in `.env`, it performs a no-key DuckDuckGo HTML search and attempts to read up to three result pages. It uses conservative request limits, an identifying User-Agent and robots.txt checks; if robots.txt cannot be verified, it skips the page. Search requires connectivity. The research output is marked as external and the model is instructed to treat page text as untrusted, verify claims, and report source disagreements.


DATA AND PRIVACY
- Existing kenzie_memory.db / kenzie_memory.json are not deleted or migrated.
- Conversation memory remains local in SQLite.
- Local inference uses the loopback Ollama endpoint.
- Research sends only the explicit search query to the search provider; it does not send the user's conversation history or stored memories.
- External providers are not automatic in this version. Legacy provider keys are retained only as commented examples in .env.example.

DIAGNOSTICS
- Check Ollama: ollama --version, ollama list, ollama ps
- Check model: ollama show qwen2.5:1.5b
- Run a prompt directly: ollama run qwen2.5:1.5b "Responda brevemente: o que é água?"
- Kenzie terminal labels: [IA LOCAL] for generation, [Cognition] for cognitive pipeline.
- Disable cognitive analysis: KENZIE_COGNITION_ENABLED=0
- Disable research: KENZIE_RESEARCH_ENABLED=0
- Disable processing voice: KENZIE_THINKING_VOICE=0

TESTS
Run: python -m unittest discover -s tests -v
Unit tests are not the same as hardware/model integration tests. Read LOCAL_ENGINE_09.md for limitations and outstanding real-device checks.


ARCHITECTURE
Kenzie.py -> Orchestrator -> Cognitive Bridge/Core, local inference, memory, Action Engine.
LocalInferenceEngine is a backend interface around Ollama's OpenAI-compatible localhost API.
ResearchEngine is a separate network capability; it does not act as the response generator.
Learning remains candidate/review based and does not alter model weights.
TXT
cat > cognitive_bridge.py.tmp <<'TXT'
