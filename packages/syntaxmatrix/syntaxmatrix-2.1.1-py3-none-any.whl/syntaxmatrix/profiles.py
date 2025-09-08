# syntaxmatrix/profiles.py
from openai import OpenAI
from google import genai

from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}
for p in list_profiles():
    prof = load_profile(p["name"])
    if prof:
        _profiles[p["purpose"]] = prof


def get_profile(purpose: str) -> dict:
    """
    Return the full profile dict {'provider'=val, 'api_key'=val, 'model'=val} for that purpose (eg. "chat", "coding", etc).
    Returns None if no such profile exists.
    """
    prof = _profiles.get(purpose, None)
    return prof


def get_client(profile):
    
    provider = profile["provider"].lower()
    api_key = profile["api_key"]

    if provider == "openai":
        return OpenAI(api_key=api_key)
    if provider == "google":
        return  genai.Client(api_key=api_key)
    if provider == "xai":
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    if provider == "deepseek":
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    if provider == "moonshotai":
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
    if provider == "alibaba":
        return OpenAI(api_key=api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",)