import os
import json
import re
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote
from PySide6.QtWidgets import QApplication
print("INTERFACE IMPORTADA")
from interface import KenzieInterface
import sys
import threading

from dotenv import load_dotenv
from openai import OpenAI

import tools
from memory_store import MemoryStore
from personality import PERSONALITY_PROMPT
from voice import VoiceManager

# ============================================================
# KENZIE v0.3
# Assistente pessoal para Windows 10
#
# Recursos:
# - Memória permanente
# - Modo offline
# - IA online opcional
# - Controle básico do Windows
# - Abertura de programas
# - Abertura de sites
# - Pesquisa na internet
# - Comandos naturais
# ============================================================


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Carrega o .env a partir da pasta deste arquivo, não da pasta atual do CMD.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_FILE, override=False)

API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter atende conversas gerais; Ollama fica reservado para programação.
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").strip().lower() in ("1", "true", "yes", "sim")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_CODER_MODEL = os.getenv("OLLAMA_CODER_MODEL", "qwen2.5-coder:1.5b")

ollama_client = None
openrouter_client = None
openai_client = None

if OLLAMA_ENABLED:
    try:
        ollama_client = OpenAI(
            api_key="ollama-local",
            base_url=OLLAMA_BASE_URL,
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "120"))
        )
    except Exception as error:
        print(f"Não foi possível inicializar o cliente Ollama: {error}")

if OPENROUTER_API_KEY:
    try:
        openrouter_client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://openrouter.ai/",
                "X-Title": "Kenzie Assistant"
            },
            timeout=60.0
        )
    except Exception as error:
        print(f"Não foi possível inicializar a OpenRouter: {error}")

if API_KEY:
    try:
        openai_client = OpenAI(api_key=API_KEY, timeout=60.0)
    except Exception as error:
        print(f"Não foi possível inicializar a OpenAI: {error}")

# Mantém compatibilidade com as verificações antigas do projeto.
client = openrouter_client or openai_client or ollama_client
AI_PROVIDER = "openrouter" if openrouter_client else ("openai" if openai_client else ("ollama" if ollama_client else "offline"))
AI_MODEL = (os.getenv("OPENROUTER_MODEL", "openrouter/free") if openrouter_client else (os.getenv("OPENAI_MODEL", "gpt-4o-mini") if openai_client else OLLAMA_CODER_MODEL))


MEMORY_FILE = os.path.join(BASE_DIR, "kenzie_memory.json")
MEMORY_DB = os.path.join(BASE_DIR, "kenzie_memory.db")
memory_store = MemoryStore(MEMORY_DB)

MAX_MESSAGES = 20
conversation = memory_store.get_recent_messages(MAX_MESSAGES)
KENZIE_STATE = "STANDBY"

INTERFACE = None
VOICE = VoiceManager(rate=int(os.getenv("KENZIE_VOICE_RATE", "175")), volume=float(os.getenv("KENZIE_VOICE_VOLUME", "0.95")), base_dir=BASE_DIR, profile=os.getenv("KENZIE_VOICE_PROFILE", "TARS"))

def atualizar_interface():
    if INTERFACE is not None:
        INTERFACE.nucleo_central.mudar_estado(KENZIE_STATE.lower())
def enviar_para_interface(mensagem):
    if INTERFACE is not None:
        INTERFACE.adicionar_mensagem(mensagem)


# ============================================================
# PERSONALIDADE
# ============================================================

SYSTEM_PROMPT = """
IDENTIDADE FIXA:
- Seu nome é Kenzie. Apresente-se sempre como Kenzie quando perguntarem sua identidade.
- Você é a camada de inteligência artificial da assistente Kenzie para Windows 10, responsável por compreender pedidos, conversar e decidir quando usar as ferramentas disponíveis.
- Você faz parte do projeto Kenzie. Não diga que está apenas "na Kenzie" como se fosse uma pessoa externa: você é a própria inteligência conversacional da assistente.
- O nome do usuário, a forma de tratamento preferida e os fatos do projeto podem estar disponíveis na seção MEMÓRIA PERSISTENTE. Use-os naturalmente em TODAS as respostas.
- Se a memória indicar uma forma de tratamento, respeite-a consistentemente. Se indicar "senhor", trate o usuário por "senhor"; não use o primeiro nome como vocativo, a menos que ele peça.
- Se a memória indicar o nome completo do usuário, use esse dado quando perguntarem o nome dele.

PERSONALIDADE:
- Inteligente, natural, confiante e prestativa.
- Informal na medida certa, com ironia sutil quando combinar com a conversa.
- Objetiva e clara, sem parecer fria ou excessivamente formal.
- Não use emojis, emoticons ou símbolos decorativos nas respostas.

ESTILO DE RESPOSTA:
1. Responda em português quando o usuário falar português.
2. Para perguntas simples, responda em poucas frases.
3. Para perguntas complexas, organize a resposta em tópicos quando isso ajudar.
4. Evite repetir a pergunta, introduções desnecessárias e conclusões redundantes.
5. Nunca transforme a pergunta do usuário em parte da resposta.
6. Não invente informações. Se um dado não estiver no contexto ou na memória, diga que ainda não sabe.

REGRAS DE FUNCIONAMENTO:
1. Nunca afirme que executou uma ação sem que ela tenha sido concluída.
2. Não execute ações perigosas sem confirmação.
3. Avise quando uma capacidade ainda não estiver implementada.
4. Não afirme que possui acesso a arquivos, dispositivos ou recursos que não consegue acessar.
5. Use as ferramentas disponíveis quando o pedido exigir uma ação local e a ferramenta corresponder ao pedido.
"""


# ============================================================
# MEMÓRIA
# ============================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {}

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            loaded = json.load(file)

        if not isinstance(loaded, dict):
            return {}

        # Migra automaticamente a memória criada pela versão anterior,
        # que podia salvar a frase inteira no campo "nome".
        old_name = loaded.get("nome")
        if isinstance(old_name, str):
            name_match = re.match(
                r"^(.+?)\s+e\s+(?:estou|sou|trabalho|desenvolvo|faço|faco)\b",
                old_name,
                flags=re.IGNORECASE
            )
            if name_match:
                loaded["nome"] = name_match.group(1).strip()
                old_project = re.search(
                    r"projeto\s+chamado\s+([^,.!?;]+)",
                    old_name,
                    flags=re.IGNORECASE
                )
                if old_project and not loaded.get("projeto"):
                    loaded["projeto"] = old_project.group(1).strip()
                    loaded["descricao_projeto"] = (
                        "Assistente pessoal de IA para Windows 10, com interface própria, "
                        "conversação e ferramentas para executar tarefas locais."
                    )

        # O banco SQLite é a fonte persistente principal; JSON permanece como backup.
        try:
            loaded.update(memory_store.get_all_facts())
        except Exception as memory_error:
            print(f"Não foi possível consultar a memória SQLite: {memory_error}")
        return loaded

    except Exception:
        try:
            return memory_store.get_all_facts()
        except Exception:
            return {}


def save_memory(memory):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                ensure_ascii=False,
                indent=4
            )

        memory_store.set_facts(memory)
        return True

    except Exception as error:
        print(f"Erro ao salvar memória: {error}")
        try:
            memory_store.set_facts(memory)
            return True
        except Exception:
            return False


memory = load_memory()
# Migra automaticamente os fatos do JSON antigo para o banco SQLite.
try:
    memory_store.set_facts(memory)
except Exception as migration_error:
    print(f"Não foi possível migrar a memória antiga: {migration_error}")


def show_memory():

    if not memory:

        return "Minha memória está vazia."

    result = "Estas são as informações que lembro:\n\n"

    for key, value in memory.items():

        result += f"- {key}: {value}\n"

    return result


# ============================================================
# CONTEXTO
# ============================================================

def add_user_message(message):

    conversation.append({"role": "user", "content": message})
    memory_store.add_message("user", message)
    limit_context()


def add_assistant_message(message):

    conversation.append({"role": "assistant", "content": message})
    memory_store.add_message("assistant", message)
    limit_context()


def limit_context():

    if len(conversation) > MAX_MESSAGES:

        del conversation[:-MAX_MESSAGES]


def clear_context():

    conversation.clear()
    # ============================================================
# ATIVAÇÃO DA KENZIE
# ============================================================
def detectar_ativacao(message):
    global KENZIE_STATE

    text = message.strip().lower()

    if (
        "kenzie, está acordada" in text
        or "kenzie, esta acordada" in text
    ):
        KENZIE_STATE = "LEVE"
        atualizar_interface()
        return "LEVE"

    if "kenzie, vamos trabalhar" in text:
        KENZIE_STATE = "COMPLETO"
        atualizar_interface()
        return "COMPLETO"

    if "kenzie, pode dormir" in text:
        KENZIE_STATE = "STANDBY"
        atualizar_interface()
        return "STANDBY"

    return None
# ============================================================
# INFORMAÇÕES DO SISTEMA
# ============================================================

def get_time():

    return datetime.now().strftime("%H:%M:%S")


def get_date():

    return datetime.now().strftime("%d/%m/%Y")
# ============================================================
# VOZ - TEXT TO SPEECH
# ============================================================

def falar(texto):
    """Enfileira uma resposta para reprodução sem bloquear a interface."""
    try:
        VOICE.speak(texto)
    except Exception as error:
        print(f"Erro na voz: {error}")


# ============================================================
# ABRIR PROGRAMAS
# ============================================================

def open_calculator():

    try:

        subprocess.Popen("calc.exe")

        return "Calculadora aberta."

    except Exception as error:

        return f"Não consegui abrir a calculadora: {error}"


def open_notepad():

    try:

        subprocess.Popen("notepad.exe")

        return "Bloco de Notas aberto."

    except Exception as error:

        return f"Não consegui abrir o Bloco de Notas: {error}"


def open_paint():

    try:

        subprocess.Popen("mspaint.exe")

        return "Paint aberto."

    except Exception as error:

        return f"Não consegui abrir o Paint: {error}"


def open_explorer():

    try:

        subprocess.Popen("explorer.exe")

        return "Explorador de Arquivos aberto."

    except Exception as error:

        return f"Não consegui abrir o Explorador: {error}"


def open_task_manager():

    try:

        subprocess.Popen("taskmgr.exe")

        return "Gerenciador de Tarefas aberto."

    except Exception as error:

        return f"Não consegui abrir o Gerenciador de Tarefas: {error}"


# ============================================================
# SITES
# ============================================================

def open_google():

    webbrowser.open("https://www.google.com")

    return "Google aberto."


def open_youtube():

    webbrowser.open("https://www.youtube.com")

    return "YouTube aberto."


def open_github():

    webbrowser.open("https://github.com")

    return "GitHub aberto."


def search_google(query):

    url = (
        "https://www.google.com/search?q="
        + quote(query)
    )

    webbrowser.open(url)

    return f"Pesquisando por: {query}"


# ============================================================
# DOCUMENTOS
# ============================================================

def list_documents():

    documents = os.path.join(
        os.path.expanduser("~"),
        "Documents"
    )

    if not os.path.exists(documents):

        return "A pasta Documentos não foi encontrada."

    try:

        files = os.listdir(documents)

        if not files:

            return "A pasta Documentos está vazia."

        result = "Arquivos encontrados:\n\n"

        for file in files[:50]:

            result += f"- {file}\n"

        return result

    except Exception as error:

        return f"Não consegui acessar Documentos: {error}"


# ============================================================
# SISTEMA
# ============================================================

def lock_computer():

    try:

        subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"],
            check=False
        )

        return "Computador bloqueado."

    except Exception as error:

        return f"Não consegui bloquear o computador: {error}"


# ============================================================
# MEMÓRIA
# ============================================================

def process_memory_command(command):
    """Interpreta fatos simples e comandos explícitos de memória."""
    text = command.strip()
    lower = text.lower()
    changed = False

    # Nome do usuário: aceita declarações e instruções explícitas.
    name_patterns = [
        r"\bmeu nome\s+(?:é|e)\s+(.+?)(?=\s+e\s+(?:estou|sou|trabalho|estudo|desenvolvo|faço|faco|me\s+chame|me\s+trate)\b|[,.;!?]|$)",
        r"\bme chamo\s+(.+?)(?=[,.;!?]|$)",
        r"\batribua meu nome a\s+(.+?)(?=\s+e\s+(?:me\s+chame|me\s+trate)\b|[,.;!?]|$)",
        r"\bmeu nome completo é\s+(.+?)(?=[,.;!?]|$)"
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text, flags=re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip().strip(" \t\"'")
            if name:
                memory["nome"] = name
                changed = True
            break

    # Forma de tratamento preferida.
    address_patterns = [
        r"\bme chame de\s+([^,.!?;]+)",
        r"\bme trate por\s+([^,.!?;]+)",
        r"\bquero ser chamado de\s+([^,.!?;]+)",
        r"\bquero que me chame de\s+([^,.!?;]+)"
    ]
    for pattern in address_patterns:
        address_match = re.search(pattern, text, flags=re.IGNORECASE)
        if address_match:
            form = address_match.group(1).strip().strip(" \t\"'")
            if form:
                memory["tratamento"] = form
                changed = True
            break

    # Identifica o nome do projeto quando ele é mencionado explicitamente.
    project_match = re.search(
        r"\bprojeto\s+chamado\s+([^,.!?;]+)",
        text,
        flags=re.IGNORECASE
    )
    if project_match:
        project_name = project_match.group(1).strip().strip(" \t\"'")
        if project_name:
            memory["projeto"] = project_name
            if "desenvolvendo" in lower or "desenvolvo" in lower:
                memory["descricao_projeto"] = (
                    "Assistente pessoal de IA para Windows 10, com interface própria, "
                    "conversação e ferramentas para executar tarefas locais."
                )
            changed = True

    if "você agora faz parte desse projeto" in lower or "voce agora faz parte desse projeto" in lower:
        memory["papel_kenzie"] = (
            "IA principal integrada à assistente Kenzie, responsável pela conversação "
            "e pela interpretação dos pedidos do usuário."
        )
        changed = True

    if (
        "atribua o nome kenzie a si mesmo" in lower
        or "seu nome agora é kenzie" in lower
        or "seu nome agora e kenzie" in lower
    ):
        memory["nome_assistente"] = "Kenzie"
        changed = True

    # Comando explícito para guardar uma informação livre.
    remember_match = re.match(r"(?:lembre que|guarde que|salve que)\s+(.+)$", text, re.IGNORECASE)
    if remember_match:
        value = remember_match.group(1).strip()
        if value:
            key = f"informação_{len([k for k in memory if k.startswith('informação_')]) + 1}"
            memory[key] = value
            changed = True

    if changed:
        saved = save_memory(memory)
        # Registra também a interação para que a conversa continue coerente.
        add_user_message(text)
        reply = "Entendi. Salvei essa informação na minha memória." if saved else "Entendi a informação, mas não consegui gravá-la no arquivo de memória."
        add_assistant_message(reply)
        return reply

    # Consultas de memória estruturada.
    if (
        "o que você lembra" in lower or "o que voce lembra" in lower
        or "mostre sua memória" in lower or "mostre sua memoria" in lower
        or "o que está salvo" in lower or "o que esta salvo" in lower
    ):
        reply = show_memory()
        add_user_message(text)
        add_assistant_message(reply)
        return reply

    if ("como você deve me chamar" in lower or "como voce deve me chamar" in lower
            or "qual tratamento" in lower or "como devo ser chamado" in lower):
        form = memory.get("tratamento")
        reply = f"Devo chamar você de {form}." if form else "Ainda não tenho uma forma de tratamento preferida salva."
        add_user_message(text)
        add_assistant_message(reply)
        return reply

    if re.search(r"\bqual (?:é|e) meu nome\b|\bvocê sabe meu nome\b|\bvoce sabe meu nome\b", lower):
        reply = f"Seu nome é {memory['nome']}." if memory.get("nome") else "Ainda não sei seu nome."
        add_user_message(text)
        add_assistant_message(reply)
        return reply

    if (
        "nome do projeto" in lower or "qual é o projeto" in lower
        or "qual e o projeto" in lower or "o que estamos fazendo" in lower
        or "o que estamos desenvolvendo" in lower
    ):
        project = memory.get("projeto")
        if project:
            details = memory.get("descricao_projeto", "")
            role = memory.get("papel_kenzie", "")
            reply = f"O projeto se chama {project}."
            if details:
                reply += f" Estamos desenvolvendo uma assistente pessoal de IA para Windows 10, com interface própria e ferramentas locais."
            if role:
                reply += f" Meu papel é ser a inteligência conversacional integrada a ela."
        else:
            reply = "Ainda não tenho o nome do projeto salvo na memória."
        add_user_message(text)
        add_assistant_message(reply)
        return reply

    return None

# ============================================================
# COMANDOS LOCAIS
# ============================================================

def process_local_command(command):

    text = command.strip().lower()
    # Normalize trailing punctuation so conversational commands such as
    # "diagnóstico de arquivo inexistente." match the local handler.
    text = text.rstrip(" .!?;,:\t")


    # ========================================================
    # REMOVE "KENZIE" DO COMANDO
    # ========================================================

    if text.startswith("kenzie"):

        text = text[6:].strip()

        if text.startswith(","):

            text = text[1:].strip()


    # ========================================================
    # TESTE CONTROLADO DE FALHA (diagnóstico offline)
    # ========================================================

    if text in ("diagnostico de falha", "diagnóstico de falha", "diagnostico de arquivo inexistente", "diagnóstico de arquivo inexistente"):
        # Falha intencional para verificar se o Worker e a interface
        # encaminham exceções para o estado ERROR do núcleo.
        with open("diagnostico_404.tmp", "r", encoding="utf-8") as _arquivo:
            _arquivo.read()

        return "O arquivo de diagnóstico foi encontrado (teste inesperado)."



    # ========================================================
    # SAIR
    # ========================================================

    if text in [
        "sair",
        "exit",
        "quit",
        "encerrar",
        "fechar"
    ]:

        return "__EXIT__"


    # ========================================================
    # LIMPAR CONVERSA
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "limpar conversa",
            "limpe a conversa",
            "apagar conversa",
            "resetar conversa"
        ]
    ):

        return "__CLEAR__"


    # ========================================================
    # HORA
    # ========================================================

    if (
        "que horas" in text
        or "qual a hora" in text
        or text == "hora"
    ):

        return f"Agora são {tools.get_time()}."


    # ========================================================
    # DATA
    # ========================================================

    if (
        "qual a data" in text
        or "qual é a data" in text
        or "que dia é hoje" in text
        or "que dia e hoje" in text
        or text == "data"
    ):

        return f"Hoje é {tools.get_date()}."


    # ========================================================
    # ABRIR PROGRAMAS
    # ========================================================

    open_words = [
        "abra",
        "abrir",
        "abre",
        "inicie",
        "iniciar",
        "execute",
        "executar",
        "rode",
        "rodar"
    ]


    # ========================================================
    # CALCULADORA
    # ========================================================

    if "calculadora" in text:

        if any(word in text for word in open_words):

            return tools.open_calculator()


    # ========================================================
    # PAINT
    # ========================================================

    if "paint" in text:

        if any(word in text for word in open_words):

            return tools.open_paint()


    # ========================================================
    # BLOCO DE NOTAS
    # ========================================================

    if (
        "bloco de notas" in text
        or "notepad" in text
    ):

        if any(word in text for word in open_words):

            return tools.open_notepad()


    # ========================================================
    # EXPLORADOR
    # ========================================================

    if (
        "explorador" in text
        or "explorer" in text
    ):

        if any(word in text for word in open_words):

            return tools.open_explorer()


    # ========================================================
    # GERENCIADOR DE TAREFAS
    # ========================================================

    if (
        "gerenciador de tarefas" in text
        or "task manager" in text
    ):

        if any(word in text for word in open_words):

            return tools.open_task_manager()


    # ========================================================
    # GOOGLE
    # ========================================================

    if "google" in text:

        if any(
            word in text
            for word in [
                "abra",
                "abrir",
                "abre",
                "acesse",
                "acessar"
            ]
        ):

            return tools.open_google()


    # ========================================================
    # YOUTUBE
    # ========================================================

    if "youtube" in text:

        if any(
            word in text
            for word in [
                "abra",
                "abrir",
                "abre",
                "acesse",
                "acessar"
            ]
        ):

            return tools.open_youtube()


    # ========================================================
    # GITHUB
    # ========================================================

    if "github" in text:

        if any(
            word in text
            for word in [
                "abra",
                "abrir",
                "abre",
                "acesse",
                "acessar"
            ]
        ):

            return tools.open_github()


    # ========================================================
    # PESQUISA
    # ========================================================

    search_prefixes = [

        "pesquise ",

        "pesquisa ",

        "procure ",

        "buscar ",

        "busque ",

        "pesquisa no google ",

        "pesquise no google "

    ]


    for prefix in search_prefixes:

        if text.startswith(prefix):

            query = text[len(prefix):].strip()

            if query:

                return tools.search_google(query)


    # ========================================================
    # DOCUMENTOS
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "liste meus documentos",
            "listar documentos",
            "mostre meus documentos",
            "ver meus documentos",
            "mostrar documentos"
        ]
    ):

        return tools.list_documents()


    # ========================================================
    # BLOQUEAR COMPUTADOR
    # ========================================================

    if any(
        phrase in text
        for phrase in [
            "bloqueie o computador",
            "bloquear computador",
            "bloqueia o computador",
            "trave o computador",
            "travar computador"
        ]
    ):

        return tools.lock_computer()


    # ========================================================
    # LISTAR PROGRAMAS
    # ========================================================

    if (
        "liste meus programas" in text
        or "listar programas" in text
        or "quais programas eu tenho" in text
        or "programas instalados" in text
    ):

        return tools.list_programs()


    # ========================================================
    # ABRIR PROGRAMA
    # ========================================================

    open_phrases = [
        "abra ",
        "abrir ",
        "abre ",
        "inicie ",
        "iniciar ",
        "execute ",
        "executar "
    ]


    for phrase in open_phrases:

        if text.startswith(phrase):

            program_name = text[
                len(phrase):
            ].strip()


            # Evita que essa parte tente
            # abrir os programas que já possuem
            # comandos específicos.

            known_programs = [
                "calculadora",
                "paint",
                "bloco de notas",
                "notepad",
                "explorador",
                "explorer",
                "gerenciador de tarefas",
                "google",
                "youtube",
                "github"
            ]


            if program_name in known_programs:

                break


            # Só tenta abrir nomes reconhecidos pelo sistema. Frases
            # longas/imperativas desconhecidas não são lançadas ao menu Iniciar.
            if program_name:
                return None
                    # ========================================================
    # PASTA DOCUMENTOS
    # ========================================================

    if (
        "abra documentos" in text
        or "abrir documentos" in text
        or "abre documentos" in text
        or "abra minha pasta documentos" in text
        or "abrir minha pasta documentos" in text
    ):

        return tools.open_documents()


    # ========================================================
    # PASTA DOWNLOADS
    # ========================================================

    if (
        "abra downloads" in text
        or "abrir downloads" in text
        or "abre downloads" in text
        or "abra minha pasta downloads" in text
        or "abrir minha pasta downloads" in text
    ):

        return tools.open_downloads()


    # ========================================================
    # ÁREA DE TRABALHO
    # ========================================================

    if (
        "abra a área de trabalho" in text
        or "abra a area de trabalho" in text
        or "abrir área de trabalho" in text
        or "abrir area de trabalho" in text
    ):

        return tools.open_desktop()


    # ========================================================
    # LISTAR DOWNLOADS
    # ========================================================

    if (
        "liste meus downloads" in text
        or "listar downloads" in text
        or "mostre meus downloads" in text
    ):

        return tools.list_downloads()


    # ========================================================
    # CRIAR PASTA
    # ========================================================

    create_prefixes = [
        "crie uma pasta chamada ",
        "criar uma pasta chamada ",
        "crie a pasta ",
        "criar a pasta "
    ]

    for prefix in create_prefixes:

        if text.startswith(prefix):

            folder_name = text[len(prefix):].strip()

            if folder_name:

                return tools.create_folder(
                    folder_name
                )
                    # ========================================================
    # VOLUME
    # ========================================================

    if (
        "aumente o volume" in text
        or "aumentar o volume" in text
        or "aumenta o volume" in text
        or "volume mais alto" in text
    ):

        return tools.increase_volume()


    if (
        "diminua o volume" in text
        or "diminuir o volume" in text
        or "diminui o volume" in text
        or "volume mais baixo" in text
    ):

        return tools.decrease_volume()


    if (
        "silencie o computador" in text
        or "silenciar computador" in text
        or "coloque no mudo" in text
        or "coloque o computador no mudo" in text
    ):

        return tools.mute_volume()


    if (
        "tire do mudo" in text
        or "tirar do mudo" in text
        or "ative o som" in text
        or "ativar o som" in text
    ):

        return tools.unmute_volume()


    # ========================================================
    # VOLUME EM PORCENTAGEM
    # ========================================================

    if "volume" in text and "%" in text:

        try:

            before = text.split("%")[0]

            number = ""

            for character in reversed(before):

                if character.isdigit():

                    number = character + number

                elif number:

                    break

            if number:

                return tools.set_volume(
                    int(number)
                )

        except Exception:

            pass
            # ========================================================
    # CONTROLE DE JANELAS
    # ========================================================

    if (
        "mostre a área de trabalho" in text
        or "mostre a area de trabalho" in text
        or "mostrar área de trabalho" in text
        or "mostrar area de trabalho" in text
        or "desktop" == text
    ):

        return tools.show_desktop()


    if (
        "minimize tudo" in text
        or "minimizar tudo" in text
        or "minimize todas as janelas" in text
        or "minimizar todas as janelas" in text
    ):

        return tools.minimize_all_windows()
        # ========================================================
    # CAPTURA DA TELA
    # ========================================================

    if (
        "tire um print" in text
        or "tirar um print" in text
        or "tire print" in text
        or "captura da tela" in text
        or "capture a tela" in text
        or "tire uma captura" in text
    ):

        return tools.screenshot()
        # ========================================================
    # VISÃO
    # ========================================================

        if (
        "capture minha tela" in text
        or "capture a minha tela" in text
        or "tire uma foto da tela" in text
        or "tire um print da tela" in text
        or "analise minha tela" in text
    ):

            result = tools.get_screen_info()

        if result:

            return (
                f"Captura realizada. "
                f"Resolução: {result['width']}x{result['height']}. "
                f"Arquivo salvo na Área de Trabalho."
            )

        return "Não consegui capturar a tela."
    # ========================================================
    # NENHUM COMANDO ENCONTRADO
    # ========================================================

    return None
# ============================================================
# MODO OFFLINE
# ============================================================

def offline_response(message):

    text = message.lower().strip()


    if text in [
        "oi",
        "olá",
        "ola",
        "oi kenzie",
        "olá kenzie",
        "ola kenzie"
    ]:

        return (
            "Olá! Eu sou a Kenzie. "
            "Estou funcionando em modo offline."
        )


    if (
        "quem é você" in text
        or "quem e voce" in text
    ):

        return (
            "Eu sou a Kenzie, sua assistente pessoal."
        )


    if (
        "como você está" in text
        or "como voce esta" in text
    ):

        return "Estou funcionando normalmente."


    if (
        "obrigado" in text
        or "obrigada" in text
    ):

        return "Por nada."


    if "ajuda" in text:

        return (
            "Posso controlar algumas funções do Windows, "
            "abrir programas e sites, pesquisar na internet, "
            "consultar hora e data e usar minha memória."
        )


    return (
        "Estou funcionando offline no momento. "
        "Ainda não tenho um modelo de IA disponível "
        "para responder perguntas complexas."
    )


# ============================================================
# IA
# ============================================================

def tarefa_de_programacao(message):
    """Detecta pedidos de programação para encaminhá-los ao modelo local especializado."""
    texto = str(message).lower()
    termos_codigo = (
        "código", "codigo", "python", "java", "javascript", "html", "css",
        "sql", "debug", "depurar", "traceback", "exception", "função", "funcao",
        "classe", "script", "programação", "programacao", "programar", "refatorar",
        "api", "biblioteca", "pip install", "terminal", "cmd", "erro no código",
        "corrija esse código", "corrigir código", "implemente", "compile"
    )
    return any(t in texto for t in termos_codigo)


def montar_mensagens_ia(message):
    add_user_message(message)
    memory_text = (
        "\n\nMEMÓRIA PERSISTENTE RECUPERADA DO BANCO LOCAL (SQLite):\n"
        + memory_store.build_prompt_memory(message)
        + "\n\nUse esses dados quando forem relevantes. Não invente lembranças.\n"
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + PERSONALITY_PROMPT + memory_text}]
    messages.extend(conversation[-MAX_MESSAGES:])
    return messages


def extrair_resposta(response):
    if not response.choices:
        return None, None
    choice = response.choices[0]
    answer_message = choice.message
    tool_calls = answer_message.tool_calls or []
    if tool_calls:
        tool_call = tool_calls[0]
        tool_name = tool_call.function.name
        result = use_tool(tool_name)
        add_assistant_message(str(result))
        return str(result), "tool"
    answer = answer_message.content
    if isinstance(answer, list):
        answer = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in answer
        )
    if not answer or not str(answer).strip():
        return None, choice.finish_reason or "desconhecido"
    answer = str(answer).strip()
    add_assistant_message(answer)
    return answer, None


def ask_ai(message):
    messages = montar_mensagens_ia(message)
    erros = []
    eh_codigo = tarefa_de_programacao(message)

    # Programação: tenta somente o Qwen Coder local. Não tenta modelos removidos.
    if eh_codigo and ollama_client is not None:
        try:
            print(f"[IA] Ollama local: {OLLAMA_CODER_MODEL} (programação)")
            response = ollama_client.chat.completions.create(
                model=OLLAMA_CODER_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=900,
                tools=AI_TOOLS
            )
            answer, detail = extrair_resposta(response)
            if answer:
                print(f"[IA] Resposta concluída com Ollama/{OLLAMA_CODER_MODEL}")
                return answer
            erros.append(f"Ollama/{OLLAMA_CODER_MODEL}: resposta vazia ({detail})")
        except Exception as error:
            erros.append(f"Ollama/{OLLAMA_CODER_MODEL}: {error}")
            print(f"[IA] Falha no modelo local de programação: {error}")

    # Conversa geral vai direto para a OpenRouter, sem esperar o Ollama.
    online_client = openrouter_client or openai_client
    online_model = (
        os.getenv("OPENROUTER_MODEL", "openrouter/free") if openrouter_client
        else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    online_name = "openrouter" if openrouter_client else "openai"
    if online_client is not None:
        try:
            print(f"[IA] {online_name}: {online_model}" + (" (fallback)" if eh_codigo else " (conversa geral)"))
            response = online_client.chat.completions.create(
                model=online_model,
                messages=messages,
                temperature=0.7,
                max_tokens=900,
                tools=AI_TOOLS
            )
            answer, detail = extrair_resposta(response)
            if answer:
                print(f"[IA] Resposta concluída com {online_name}/{online_model}")
                return answer
            erros.append(f"{online_name}: resposta vazia ({detail})")
        except Exception as error:
            erros.append(f"{online_name}: {error}")
            print(f"[IA] Falha em {online_name}: {error}")

    # Se a OpenRouter não estiver configurada, o modelo local pode atender como reserva.
    if not eh_codigo and ollama_client is not None:
        try:
            print(f"[IA] Reserva local: {OLLAMA_CODER_MODEL}")
            response = ollama_client.chat.completions.create(
                model=OLLAMA_CODER_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=500
            )
            answer, detail = extrair_resposta(response)
            if answer:
                return answer
            erros.append(f"Ollama reserva: resposta vazia ({detail})")
        except Exception as error:
            erros.append(f"Ollama reserva: {error}")

    if erros:
        print("[IA] Todos os provedores falharam: " + " | ".join(erros))
    return offline_response(message)

def comando_permitido(message):
    if KENZIE_STATE == "STANDBY":
        return False

    if KENZIE_STATE == "LEVE":
        comandos_leves = [
            "calculadora",
            "paint",
            "bloco de notas",
            "notepad",
            "explorador",
            "google",
            "youtube",
            "github",
            "pesquise",
            "pesquisa",
            "procure",
            "buscar",
            "busque",
            "que horas",
            "qual a hora",
            "qual a data",
            "que dia é hoje",
            "volume"
        ]

        text = message.lower()

        return any(comando in text for comando in comandos_leves)

    return True

def process_command(message):

    if not comando_permitido(message):

        if KENZIE_STATE == "STANDBY":
            return "Estou em espera. Diga uma frase de ativação para me chamar."

        if KENZIE_STATE == "LEVE":
            return "Esse comando está disponível apenas no modo COMPLETO."

        return "Comando não permitido."

    # MEMÓRIA
    memory_result = process_memory_command(message)

    if memory_result is not None:
        return memory_result

    # COMANDOS LOCAIS
    local_result = process_local_command(message)

    if local_result is not None:
        return local_result

    # IA
    return ask_ai(message)
    # ============================================================
# FERRAMENTAS DA KENZIE
# ============================================================

TOOLS = {
    "calculadora": tools.open_calculator,
    "paint": tools.open_paint,
    "bloco_de_notas": tools.open_notepad,
    "explorador": tools.open_explorer,
    "gerenciador_de_tarefas": tools.open_task_manager,
    "google": tools.open_google,
    "youtube": tools.open_youtube,
    "github": tools.open_github,
    "documentos": tools.list_documents,
    "downloads": tools.list_downloads,
    "bloquear_computador": tools.lock_computer,
}


def use_tool(tool_name):

    if tool_name not in TOOLS:
        return "Essa ferramenta não existe."

    try:
        return TOOLS[tool_name]()
    except Exception as error:
        return f"Erro ao executar a ferramenta: {error}"
# ============================================================
# DESCRIÇÃO DAS FERRAMENTAS
# ============================================================

TOOL_DESCRIPTIONS = {
    "calculadora": "Abre a calculadora do Windows.",
    "paint": "Abre o Paint.",
    "bloco_de_notas": "Abre o Bloco de Notas.",
    "explorador": "Abre o Explorador de Arquivos.",
    "gerenciador_de_tarefas": "Abre o Gerenciador de Tarefas.",
    "google": "Abre o Google no navegador.",
    "youtube": "Abre o YouTube no navegador.",
    "github": "Abre o GitHub no navegador.",
    "documentos": "Mostra os documentos do usuário.",
    "downloads": "Mostra os arquivos da pasta Downloads.",
    "bloquear_computador": "Bloqueia o computador."
}
AI_TOOLS = []

for tool_name, description in TOOL_DESCRIPTIONS.items():
    AI_TOOLS.append({
        "type": "function",
        "function": {
            "name": tool_name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    })
# ============================================================
# BANNER
# ============================================================

def show_banner():

    print()

    print("=" * 60)

    print("                     KENZIE v0.6")

    print("              ASSISTENTE PESSOAL DE IA")

    print("=" * 60)

    print()

    print("Sistema: Windows 10")

    print("Memória: ATIVA")

    if ollama_client:
        print(f"Modelo local para programação: {OLLAMA_CODER_MODEL}")
    else:
        print("Modelo local de programação: Ollama não inicializado")
    if openrouter_client:
        print("IA principal para conversas: OpenRouter configurada")
    elif openai_client:
        print("Fallback online: OpenAI configurada")
    else:
        print("Fallback online: não configurado")

    print()

    print("Kenzie online.")
    print("Como posso ajudar?")

    print()

    print("Exemplos:")

    print("  Kenzie, abra a calculadora")
    print("  Kenzie, abra o Paint")
    print("  Kenzie, abra o Google")
    print("  Kenzie, pesquise inteligência artificial")
    print("  Kenzie, abra o Explorador")
    print("  Kenzie, bloqueie o computador")
    print("  Kenzie, o que você lembra?")
    print()

    print("Digite 'sair' para encerrar.")

    print()


# ============================================================
# MAIN
# ============================================================
def main():
    print("1 - Entrou na main")
    app = QApplication(sys.argv)

    print("2 - QApplication criada")

    janela = KenzieInterface()
    global INTERFACE
    INTERFACE = janela

    print("3 - KenzieInterface criada")

    janela.show()

    print("4 - janela.show() executado")

    threading.Thread(target=terminal_loop, daemon=True).start()

    print("5 - terminal_loop iniciado")

    app.exec()

    print("6 - app encerrado")


def terminal_loop():
    show_banner()

    while True:
        try:
            user_input = input("Você: ").strip()

            if not user_input:
                continue

            # ====================================================
            # FRASES DE ATIVAÇÃO
            # ====================================================

            activation = detectar_ativacao(user_input)

            if activation == "LEVE":
                print()
                print("Kenzie: Estou acordada.")
                falar("Estou acordada.")
                print()
                continue

            if activation == "COMPLETO":
                print()
                print("Kenzie: Vamos trabalhar.")
                falar("Vamos trabalhar.")
                print()
                continue
            if activation == "STANDBY":
                print()
                print("Kenzie: Entrando em espera.")
                falar("Entrando em espera.")
                print()
                continue
            if KENZIE_STATE == "STANDBY" and activation is None:
                print()
                print("Kenzie: Estou em espera. Diga uma frase de ativação para me chamar.")
                falar("Estou em espera. Diga uma frase de ativação para me chamar.")
                print()
                continue
            

            # ====================================================
            # PROCESSAR COMANDO
            # ====================================================

            result = process_command(user_input)

            if result == "__EXIT__":
                print()
                print("Kenzie: Até logo.")
                print()
                break

            if result == "__CLEAR__":
                clear_context()
                print()
                print("Kenzie: Contexto limpo.")
                print()
                continue

            print()
            print(f"Kenzie: {result}")
            falar(result)
            print()

        except KeyboardInterrupt:
            print()
            print("Kenzie: Até logo.")
            print()
            break

        except Exception as error:
            print()
            print(
                f"Kenzie: Erro inesperado: {error}"
            )
            print()
# ============================================================
# INICIAR
# ============================================================

if __name__ == "__main__":

    print("CHEGUEI NO FINAL DO ARQUIVO")

    main()