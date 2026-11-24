"""Opt-in filtering of tools that can initiate external network/browser activity."""
import os

def _enabled(value):
    return str(value or "0").strip().lower() not in {"0", "false", "off", "no"}

def available_local_tools(tool_schema, *, research_enabled=None, browser_enabled=None):
    research = _enabled(os.getenv("KENZIE_RESEARCH_ENABLED", "0")) if research_enabled is None else bool(research_enabled)
    browser = _enabled(os.getenv("KENZIE_BROWSER_ACTIONS_ENABLED", "0")) if browser_enabled is None else bool(browser_enabled)
    result=[]
    for item in list(tool_schema or []):
        name=(item.get("function") or {}).get("name", "")
        if name == "research_web" and not research: continue
        if name in {"open_url", "search_web"} and not browser: continue
        result.append(item)
    return result
