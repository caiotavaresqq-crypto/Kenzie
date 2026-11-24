"""Best-effort, no-key web research. Respects robots.txt and conservative limits."""
from __future__ import annotations
import re
import urllib.request
import urllib.parse
import urllib.robotparser
import socket
import ipaddress
from html.parser import HTMLParser
from dataclasses import dataclass

USER_AGENT = "KenzieResearch/0.9 (+local assistant; conservative web reader)"

def _public_http_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        return False
    host = parsed.hostname.lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        return False
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
        return bool(addresses) and all(ipaddress.ip_address(addr).is_global for addr in addresses)
    except (OSError, ValueError):
        return False

class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _public_http_url(newurl) or urllib.parse.urlparse(req.full_url).hostname != urllib.parse.urlparse(newurl).hostname:
            raise urllib.error.HTTPError(newurl, code, "Redirect to non-public or cross-host address blocked", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

_SAFE_OPENER = urllib.request.build_opener(_SafeRedirectHandler)


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg", "nav", "footer", "header"}: self.skip += 1
        if tag.lower() in {"p", "br", "div", "li", "h1", "h2", "h3", "h4", "article"}: self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg", "nav", "footer", "header"} and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())
    def text(self):
        return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", " ".join(self.parts))).strip()


@dataclass
class ResearchResult:
    query: str
    results: list[dict]
    warnings: list[str]


class ResearchEngine:
    def __init__(self, timeout=8, max_results=3, max_page_chars=5000):
        self.timeout=max(3, min(int(timeout), 20)); self.max_results=max(1,min(int(max_results),5)); self.max_page_chars=max(1000,min(int(max_page_chars),8000))
    def _fetch(self, url):
        parsed=urllib.parse.urlparse(url)
        if not _public_http_url(url):
            return None, "URL não pública ou inválida; página bloqueada."
        base=f"{parsed.scheme}://{parsed.netloc}"
        robots_url=base+"/robots.txt"
        rp=urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        try:
            with _SAFE_OPENER.open(urllib.request.Request(robots_url, headers={"User-Agent":USER_AGENT}), timeout=self.timeout) as r:
                rp.parse(r.read(200000).decode("utf-8", errors="replace").splitlines())
        except Exception:
            # If robots.txt cannot be checked, conservatively skip the page.
            return None, "robots.txt não pôde ser verificado; página ignorada."
        if not rp.can_fetch(USER_AGENT, url): return None, "A página restringe acesso automatizado via robots.txt."
        req=urllib.request.Request(url, headers={"User-Agent":USER_AGENT, "Accept":"text/html"})
        try:
            with _SAFE_OPENER.open(req, timeout=self.timeout) as response:
                ctype=response.headers.get("Content-Type", "")
                if "html" not in ctype.lower(): return None, "Conteúdo não HTML, ignorado."
                raw=response.read(700000).decode("utf-8", errors="replace")
            extractor=_TextExtractor(); extractor.feed(raw)
            return extractor.text()[:self.max_page_chars], None
        except Exception as exc: return None, f"Falha ao abrir página ({type(exc).__name__})."
    def search(self, query):
        query=str(query or "").strip()
        if not query: return {"ok":False,"error":"Consulta vazia"}
        url="https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req=urllib.request.Request(url, headers={"User-Agent":USER_AGENT})
        try:
            with _SAFE_OPENER.open(req, timeout=self.timeout) as response:
                html=response.read(500000).decode("utf-8", errors="replace")
        except Exception as exc:
            return {"ok":False,"query":query,"error":f"Pesquisa indisponível ({type(exc).__name__}); confira a conexão."}
        # Parse DuckDuckGo's result-link markup without third-party packages.
        candidates=[]
        for match in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, flags=re.I|re.S):
            href=match.group(1); title=re.sub(r"<[^>]+>","",match.group(2)); title=title.replace("&amp;","&").strip()
            href=href.replace("&amp;","&")
            if href.startswith("//"): href="https:"+href
            if "duckduckgo.com/l/?" in href:
                parsed=urllib.parse.parse_qs(urllib.parse.urlparse(href).query); href=parsed.get("uddg",[href])[0]
            if href.startswith("http") and title and href not in [x["url"] for x in candidates]: candidates.append({"title":title,"url":href})
            if len(candidates)>=self.max_results: break
        if not candidates: return {"ok":False,"query":query,"error":"Nenhum resultado extraível; pesquisa HTML pode ter mudado."}
        collected=[]; warnings=[]
        for item in candidates:
            text,warning=self._fetch(item["url"])
            if warning: warnings.append(item["url"]+": "+warning)
            collected.append({**item,"content":text or "Conteúdo não obtido. Use o título e link como pista, não como fonte lida."})
        return {"ok":True,"query":query,"results":collected,"warnings":warnings,"source_type":"external_research","note":"Resultados externos são candidatos; verifique autoria, data e confiabilidade antes de tratar como fato."}
