import os
import json
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
import pyttsx3

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

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = None

if API_KEY:

    try:
        client = OpenAI(api_key=API_KEY)

    except Exception:
        client = None


MEMORY_FILE = "kenzie_memory.json"

MAX_MESSAGES = 20

conversation = []
KENZIE_STATE = "STANDBY"

INTERFACE = None

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
Você é Kenzie, uma assistente pessoal de inteligência artificial.

Personalidade:

- Inteligente
- Educada
- Natural
- Confiante
- Prestativa
- Objetiva
- Calma
- Humor sutil quando apropriado

Você está funcionando em um computador Windows 10.

Regras:

1. Responda em português quando o usuário falar português.
2. Seja natural.
3. Não invente informações.
4. Não diga que executou uma ação que não executou.
5. Não execute ações perigosas sem confirmação.
6. Utilize informações da memória quando forem relevantes.
7. Seja objetiva.
8. Avise quando alguma capacidade ainda não estiver implementada.
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

            return json.load(file)

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

        return True

    except Exception:

        return False


memory = load_memory()


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

    conversation.append({
        "role": "user",
        "content": message
    })

    limit_context()


def add_assistant_message(message):

    conversation.append({
        "role": "assistant",
        "content": message
    })

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
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.say(texto)
        engine.runAndWait()

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

    text = command.strip()

    lower = text.lower()


    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    prefixes = [
        "meu nome é ",
        "meu nome e "
    ]

    for prefix in prefixes:

        if lower.startswith(prefix):

            value = text[len(prefix):].strip()

            if value:

                memory["nome"] = value

                save_memory(memory)

                return (
                    f"Prazer, {value}. "
                    "Vou guardar seu nome."
                )


    # --------------------------------------------------------
    # LEMBRAR
    # --------------------------------------------------------

    if lower.startswith("lembre que "):

        value = text[len("lembre que "):].strip()

        if value:

            key = f"informação_{len(memory) + 1}"

            memory[key] = value

            save_memory(memory)

            return (
                "Certo. Guardei essa informação "
                "na minha memória."
            )


    # --------------------------------------------------------
    # MOSTRAR MEMÓRIA
    # --------------------------------------------------------

    if (
        "o que você lembra" in lower
        or "o que voce lembra" in lower
        or "mostre sua memória" in lower
        or "mostre sua memoria" in lower
    ):

        return show_memory()


    # --------------------------------------------------------
    # NOME
    # --------------------------------------------------------

    if (
        "qual é meu nome" in lower
        or "qual e meu nome" in lower
        or "você sabe meu nome" in lower
        or "voce sabe meu nome" in lower
    ):

        if "nome" in memory:

            return f"Seu nome é {memory['nome']}."

        return "Ainda não sei seu nome."


    return None


# ============================================================
# COMANDOS LOCAIS
# ============================================================

def process_local_command(command):

    text = command.strip().lower()


    # ========================================================
    # REMOVE "KENZIE" DO COMANDO
    # ========================================================

    if text.startswith("kenzie"):

        text = text[6:].strip()

        if text.startswith(","):

            text = text[1:].strip()


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


            if program_name:

                return tools.open_program(
                    program_name
                )
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

def ask_ai(message):

    if client is None:

        return offline_response(message)


    add_user_message(message)


    memory_text = ""

    if memory:

        memory_text = (
            "\n\nInformações lembradas:\n"
        )

        for key, value in memory.items():

            memory_text += (
                f"- {key}: {value}\n"
            )


    messages = [

        {
            "role": "system",
            "content": (
                SYSTEM_PROMPT
                + memory_text
            )
        }

    ]


    messages.extend(conversation)


    try:

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        tools=AI_TOOLS
)


        tool_calls = response.choices[0].message.tool_calls

        if tool_calls:
            tool_call = tool_calls[0]

            tool_name = tool_call.function.name

            return use_tool(tool_name)

        answer = response.choices[0].message.content

        add_assistant_message(answer)

        return answer

    except Exception as error:

        error_text = str(error)


        if "429" in error_text:

            return (
                "A IA online está sem créditos. "
                "Continuarei funcionando offline."
            )


        if "401" in error_text:

            return (
                "A chave da API não foi aceita. "
                "Verifique o arquivo .env."
            )


        return (
            "Não consegui acessar a IA agora. "
            "Posso continuar usando meus recursos offline."
        )
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

    if client:

        print("IA online: CONFIGURADA")

    else:

        print("IA online: INDISPONÍVEL")

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