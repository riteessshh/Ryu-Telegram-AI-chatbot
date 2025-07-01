import logging
from openai import OpenAI
from core.config import BASE_URL, OPENROUTER_KEY

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_KEY,
)
