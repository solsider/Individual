import asyncio
from gigachat import GigaChat
from config import GIGACHAT_CREDENTIALS

_client = GigaChat(
    credentials=GIGACHAT_CREDENTIALS,
    # если настроишь сертификат Минцифры — ставь True
    verify_ssl_certs=False,
)

def _sync_chat(prompt: str) -> str:
    resp = _client.chat(prompt)
    return resp.choices[0].message.content

async def chat(prompt: str) -> str:
    # чтобы не блокировать aiogram event loop
    return await asyncio.to_thread(_sync_chat, prompt)
