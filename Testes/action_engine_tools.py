"""Starter tool layer for Windows. Tools are allowlisted and parameter-validated."""
import os
import webbrowser
from urllib.parse import quote, urlparse
from pathlib import Path
from action_engine_models import ToolSpec


APP_ALIASES = {
    "calculadora": "calc.exe", "calculator": "calc.exe",
    "bloco de notas": "notepad.exe", "notepad": "notepad.exe",
    "paint": "mspaint.exe", "explorador de arquivos": "explorer.exe",
    "explorador": "explorer.exe", "gerenciador de tarefas": "taskmgr.exe",
    "vscode": "Visual Studio Code", "vs code": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
}
ALLOWED_SEARCH_ROOTS = [Path.home() / "Documents", Path.home() / "Desktop", Path.home() / "Downloads"]

def open_app(app_name: str) -> dict:
    app = app_name.strip().lower()
    if app not in APP_ALIASES:
        return {"ok": False, "message": f"Aplicativo '{app_name}' não está na lista autorizada para esta versão."}
    target = APP_ALIASES[app]
    try:
        if target.endswith(".exe"):
            import subprocess
            subprocess.Popen([target])
        else:
            # Import legacy module only for menu-based app discovery; it has optional audio dependencies.
            import tools as legacy_tools
            result = legacy_tools.open_program(target)
            if "não encontrei" in str(result).lower() or "não consegui" in str(result).lower():
                return {"ok": False, "message": str(result)}
        return {"ok": True, "message": f"Solicitação de abertura enviada para {app_name}."}
    except Exception as exc:
        return {"ok": False, "message": f"Falha ao abrir {app_name}: {exc}"}

def open_url(url: str) -> dict:
    if os.getenv("KENZIE_BROWSER_ACTIONS_ENABLED", "0").strip().lower() in {"0", "false", "off", "no"}:
        return {"ok": False, "message": "Abertura de navegador externo desativada pela configuração."}
    value = url.strip()
    if not value.startswith(("https://", "http://")):
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        return {"ok": False, "message": "URL inválida ou não permitida."}
    try:
        accepted = webbrowser.open(value)
        return {"ok": bool(accepted), "message": "URL encaminhada ao navegador." if accepted else "O navegador não confirmou a abertura."}
    except Exception as exc:
        return {"ok": False, "message": f"Erro ao abrir URL: {exc}"}

def search_web(query: str) -> dict:
    if os.getenv("KENZIE_BROWSER_ACTIONS_ENABLED", "0").strip().lower() in {"0", "false", "off", "no"}:
        return {"ok": False, "message": "Pesquisa pelo navegador desativada pela configuração."}
    query = query.strip()
    if not query:
        return {"ok": False, "message": "A pesquisa está vazia."}
    url = "https://www.google.com/search?q=" + quote(query)
    return open_url(url)

def research_web(query: str) -> dict:
    """Research web sources and return short extracts; does not send conversation data."""
    if os.getenv("KENZIE_RESEARCH_ENABLED", "0").strip().lower() in {"0", "false", "off", "no"}:
        return {"ok": False, "message": "Research Engine está desativado pela configuração."}
    from research_engine import ResearchEngine
    return ResearchEngine().search(query)

def search_files(query: str, max_results: int = 25) -> dict:
    query = query.strip().lower()
    if not query:
        return {"ok": False, "message": "O termo de busca está vazio."}
    max_results = max(1, min(int(max_results), 25))
    matches = []
    scanned = 0
    scan_cap = 50000
    max_depth = 6
    for root in ALLOWED_SEARCH_ROOTS:
        if not root.exists():
            continue
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                current = Path(dirpath)
                depth = len(current.relative_to(root).parts)
                if depth >= max_depth:
                    dirnames[:] = []
                # Skip hidden and common bulky/system folders.
                dirnames[:] = [d for d in dirnames if not d.startswith(".") and d.lower() not in {"node_modules", "__pycache__", "venv", "env", ".git"}]
                for filename in filenames:
                    scanned += 1
                    if query in filename.lower():
                        matches.append(str(current / filename))
                        if len(matches) >= max_results:
                            return {"ok": True, "count": len(matches), "results": matches, "limited": True, "scanned": scanned}
                    if scanned >= scan_cap:
                        return {"ok": True, "count": len(matches), "results": matches, "limited": True, "scanned": scanned, "message": "Busca interrompida pelo limite de segurança de arquivos examinados."}
        except (PermissionError, OSError):
            continue
    return {"ok": True, "count": len(matches), "results": matches, "limited": False, "scanned": scanned}

def create_tool_specs() -> list[ToolSpec]:
    schemas = {
        "open_app": {"type": "object", "properties": {"app_name": {"type": "string", "description": "Nome de um aplicativo da lista autorizada"}}, "required": ["app_name"]},
        "open_url": {"type": "object", "properties": {"url": {"type": "string", "description": "URL HTTP/HTTPS"}}, "required": ["url"]},
        "search_web": {"type": "object", "properties": {"query": {"type": "string", "description": "Assunto a pesquisar"}}, "required": ["query"]},
        "search_files": {"type": "object", "properties": {"query": {"type": "string", "description": "Trecho do nome do arquivo"}, "max_results": {"type": "integer", "description": "Limite de resultados (1-25)"}}, "required": ["query"]},
        "research_web": {"type": "object", "properties": {"query": {"type": "string", "description": "Pergunta ou assunto para pesquisa externa"}}, "required": ["query"]},
    }
    funcs = {"open_app": open_app, "open_url": open_url, "search_web": search_web, "search_files": search_files, "research_web": research_web}
    descriptions = {
        "open_app": "Abre um aplicativo na lista autorizada (Calculadora, Bloco de Notas, Paint, Explorador, Gerenciador de Tarefas, VS Code).",
        "open_url": "Abre um site por URL HTTP/HTTPS validada.",
        "search_web": "Abre uma pesquisa no Google no navegador. Não retorna resultados por conta própria.",
        "search_files": "Busca arquivos pelo nome apenas nas pastas Documentos, Área de Trabalho e Downloads, com limite de resultados.",
        "research_web": "Pesquisa na web sem API paga, tenta ler páginas respeitando robots.txt; não envia histórico ou memórias.",
    }
    permissions = {"open_app": ["app.launch"], "open_url": ["browser.open"], "search_web": ["browser.search"], "search_files": ["files.search"], "research_web": ["browser.search"]}
    return [ToolSpec(id=k, name=k, description=descriptions[k], category="local", parameters=schemas[k], required_parameters=schemas[k].get("required", []), handler=funcs[k], permissions=permissions[k]) for k in funcs]
