"""Local language-model inference backend using Ollama's OpenAI-compatible API.

No remote provider is contacted by this module. Ollama must be installed and running.
"""
from __future__ import annotations
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any


@dataclass
class LocalEngineConfig:
    base_url: str = "http://127.0.0.1:11434/v1"
    model: str = "qwen2.5:1.5b"
    temperature: float = 0.7
    max_tokens: int = 900
    timeout: float = 90.0

    @classmethod
    def from_env(cls):
        return cls(
            base_url=os.getenv("KENZIE_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/"),
            model=os.getenv("KENZIE_LOCAL_MODEL", "qwen2.5:1.5b"),
            temperature=float(os.getenv("KENZIE_LOCAL_TEMPERATURE", "0.7")),
            max_tokens=max(32, int(os.getenv("KENZIE_LOCAL_MAX_TOKENS", "900"))),
            timeout=max(5.0, float(os.getenv("KENZIE_LOCAL_TIMEOUT", "90"))),
        )


class LocalInferenceEngine:
    def __init__(self, config: LocalEngineConfig | None = None):
        self.config = config or LocalEngineConfig.from_env()
        self._client = None
        self._client_error = None
        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key="ollama-local-no-secret",
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                max_retries=0,
            )
        except Exception as exc:
            self._client_error = exc

    @property
    def client(self):
        return self._client



    def _server_model_status(self):
        if os.getenv("KENZIE_LOCAL_ENABLED", "1").strip().lower() in {"0", "false", "off", "no"}:
            return {"server_running": False, "model_available": False, "error": "Motor local desativado pela configuração."}
        host = self.config.base_url.split("/v1", 1)[0].rstrip("/")
        try:
            with urllib.request.urlopen(host + "/api/tags", timeout=3) as response:
                if response.status != 200:
                    return {"server_running": False, "model_available": False, "error": "Ollama não respondeu com status 200."}
                import json
                payload = json.loads(response.read().decode("utf-8"))
            names = set()
            for item in payload.get("models", []):
                if isinstance(item, dict):
                    names.add(str(item.get("name", "")))
                    names.add(str(item.get("model", "")))
            target = self.config.model
            available = target in names or target + ":latest" in names or target.rsplit(":", 1)[0] + ":latest" in names
            return {"server_running": True, "model_available": available, "error": None if available else f"Modelo '{target}' não está baixado."}
        except (OSError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            return {"server_running": False, "model_available": False, "error": f"Ollama local indisponível ({type(exc).__name__})."}

    def is_available(self) -> bool:
        status = self._server_model_status()
        return bool(self._client is not None and status.get("server_running") and status.get("model_available"))

    def status(self) -> dict[str, Any]:
        status = self._server_model_status()
        sdk_available = self._client is not None
        available = bool(status["server_running"] and status["model_available"] and sdk_available)
        if not sdk_available:
            error = "SDK OpenAI-compatible ausente; instale as dependências de requirements.txt."
        else:
            error = status.get("error")
        return {"available": available, "backend": "ollama", "model": self.config.model,
                "base_url": self.config.base_url, "server_running": status["server_running"],
                "model_available": status["model_available"], "sdk_available": sdk_available, "error": error}


    def generate(self, messages, *, tools=None, tool_choice="auto", temperature=None, max_tokens=None):
        if self._client is None:
            raise RuntimeError("Cliente local não inicializado. Instale a dependência openai.")
        if not self.is_available():
            details = self.status().get("error") or "Verifique Ollama, o modelo configurado e a SDK local."
            raise RuntimeError(details)
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature if temperature is None else temperature,
            "max_tokens": self.config.max_tokens if max_tokens is None else max_tokens,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
        return self._client.chat.completions.create(**params)

    def pull_model(self, model: str | None = None):
        """Explicitly request a model download from Ollama; requires network access."""
        name = model or self.config.model
        host = self.config.base_url.split("/v1", 1)[0].rstrip("/")
        import json
        request = urllib.request.Request(host + "/api/pull", data=json.dumps({"name": name, "stream": False}).encode(),
                                      headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=max(self.config.timeout, 600)) as response:
            return json.loads(response.read().decode("utf-8"))
