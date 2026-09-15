import os
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL


# ============================================================
# FERRAMENTAS DA KENZIE
# ============================================================


# ============================================================
# INFORMAÇÕES
# ============================================================

def get_time():

    return datetime.now().strftime("%H:%M:%S")


def get_date():

    return datetime.now().strftime("%d/%m/%Y")


# ============================================================
# PROGRAMAS DO WINDOWS
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


# ============================================================
# PESQUISA
# ============================================================

def search_google(query):

    url = (
        "https://www.google.com/search?q="
        + quote(query)
    )

    webbrowser.open(url)

    return f"Pesquisando por: {query}"


# ============================================================
# ARQUIVOS
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
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ],
            check=False
        )

        return "Computador bloqueado."

    except Exception as error:

        return f"Não consegui bloquear o computador: {error}"
    # ============================================================
# ARQUIVOS E PASTAS
# ============================================================

def open_documents():

    path = os.path.join(
        os.path.expanduser("~"),
        "Documents"
    )

    if os.path.exists(path):

        os.startfile(path)

        return "Abrindo sua pasta Documentos."

    return "Não encontrei a pasta Documentos."


def open_downloads():

    path = os.path.join(
        os.path.expanduser("~"),
        "Downloads"
    )

    if os.path.exists(path):

        os.startfile(path)

        return "Abrindo sua pasta Downloads."

    return "Não encontrei a pasta Downloads."


def open_desktop():

    path = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    if os.path.exists(path):

        os.startfile(path)

        return "Abrindo sua Área de Trabalho."

    return "Não encontrei a Área de Trabalho."


def list_downloads():

    path = os.path.join(
        os.path.expanduser("~"),
        "Downloads"
    )

    if not os.path.exists(path):

        return "Não encontrei a pasta Downloads."

    try:

        files = os.listdir(path)

        if not files:

            return "Sua pasta Downloads está vazia."

        result = "Arquivos em Downloads:\n\n"

        for file in files[:50]:

            result += f"- {file}\n"

        return result

    except Exception as error:

        return f"Não consegui acessar Downloads: {error}"


def create_folder(folder_name):

    desktop = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    path = os.path.join(
        desktop,
        folder_name
    )

    try:

        if os.path.exists(path):

            return f"A pasta '{folder_name}' já existe."

        os.makedirs(path)

        return f"Pasta '{folder_name}' criada na Área de Trabalho."

    except Exception as error:

        return f"Não consegui criar a pasta: {error}"
    
    # ============================================================
# CONTROLE DE VOLUME
# ============================================================

def get_volume_interface():

    devices = AudioUtilities.GetSpeakers()

    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )

    return interface.QueryInterface(
        IAudioEndpointVolume
    )


def get_volume():

    try:

        volume = get_volume_interface()

        level = volume.GetMasterVolumeLevelScalar()

        return round(level * 100)

    except Exception as error:

        return None


def set_volume(percent):

    try:

        percent = max(0, min(100, int(percent)))

        volume = get_volume_interface()

        volume.SetMasterVolumeLevelScalar(
            percent / 100,
            None
        )

        return f"Volume ajustado para {percent}%."

    except Exception as error:

        return f"Não consegui alterar o volume: {error}"


def increase_volume():

    current = get_volume()

    if current is None:

        return "Não consegui descobrir o volume atual."

    new_volume = min(100, current + 10)

    return set_volume(new_volume)


def decrease_volume():

    current = get_volume()

    if current is None:

        return "Não consegui descobrir o volume atual."

    new_volume = max(0, current - 10)

    return set_volume(new_volume)


def mute_volume():

    try:

        volume = get_volume_interface()

        volume.SetMute(1, None)

        return "Computador colocado no mudo."

    except Exception as error:

        return f"Não consegui colocar no mudo: {error}"


def unmute_volume():

    try:

        volume = get_volume_interface()

        volume.SetMute(0, None)

        return "Som ativado novamente."

    except Exception as error:

        return f"Não consegui ativar o som: {error}"
    # ============================================================
# CONTROLE DE JANELAS
# ============================================================

def show_desktop():

    try:

        # Win + D
        subprocess.run(
            [
                "powershell",
                "-Command",
                "$wshell = New-Object -ComObject WScript.Shell; $wshell.SendKeys('^{ESC}')"
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "Área de trabalho exibida."

    except Exception as error:

        return f"Não consegui mostrar a área de trabalho: {error}"


def minimize_all_windows():

    try:

        # Usa o atalho Win + D através do PowerShell
        command = (
            "$wshell = New-Object -ComObject WScript.Shell; "
            "$wshell.SendKeys('^{ESC}')"
        )

        subprocess.run(
            [
                "powershell",
                "-Command",
                command
            ],
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return "Janelas minimizadas."

    except Exception as error:

        return f"Não consegui minimizar as janelas: {error}"
# ============================================================
# VISÃO DA TELA
# ============================================================

def screenshot():

    try:

        from PIL import ImageGrab

        image = ImageGrab.grab()

        desktop = os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )

        filename = os.path.join(
            desktop,
            "kenzie_screenshot.png"
        )

        image.save(filename)

        return filename

    except Exception as error:

        return None


def get_screen_info():

    try:

        from PIL import ImageGrab

        image = ImageGrab.grab()

        width, height = image.size

        return {
            "width": width,
            "height": height,
            "file": screenshot()
        }

    except Exception as error:

        return None

# ============================================================
# DICIONÁRIO DE FERRAMENTAS
# ============================================================
# ============================================================
# DESCOBRIR PROGRAMAS DO WINDOWS
# ============================================================

def get_start_menu_programs():

    programs = {}

    locations = [

        os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs"
        ),

        os.path.join(
            os.environ.get("PROGRAMDATA", ""),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs"
        )

    ]

    for location in locations:

        if not os.path.exists(location):

            continue

        for root, dirs, files in os.walk(location):

            for file in files:

                if file.lower().endswith(".lnk"):

                    name = os.path.splitext(file)[0]

                    programs[name.lower()] = os.path.join(
                        root,
                        file
                    )

    return programs


def find_program(program_name):

    programs = get_start_menu_programs()

    search = program_name.lower().strip()

    if search in programs:

        return programs[search]

    for name, path in programs.items():

        if search in name:

            return path

    return None


def open_program(program_name):

    path = find_program(program_name)

    if path is None:

        return (
            f"Não encontrei o programa "
            f"'{program_name}' no menu Iniciar."
        )

    try:

        os.startfile(path)

        return f"Abrindo {program_name}."

    except Exception as error:

        return (
            f"Encontrei {program_name}, "
            f"mas não consegui abrir: {error}"
        )


def list_programs():

    programs = get_start_menu_programs()

    if not programs:

        return "Não encontrei programas no menu Iniciar."

    names = sorted(programs.keys())

    result = "Programas encontrados:\n\n"

    for name in names[:100]:

        result += f"- {name}\n"

    if len(names) > 100:

        result += (
            f"\n... e mais {len(names) - 100} programas."
        )

    return result

TOOLS = {

    "hora": get_time,

    "data": get_date,

    "calculadora": open_calculator,

    "bloco_de_notas": open_notepad,

    "paint": open_paint,

    "explorador": open_explorer,

    "gerenciador_de_tarefas": open_task_manager,

    "google": open_google,

    "youtube": open_youtube,

    "github": open_github,

    "documentos": list_documents,

    "bloquear_computador": lock_computer

}