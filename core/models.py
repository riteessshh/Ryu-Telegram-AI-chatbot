MODELS = {
    "gemma": "google/gemma-3n-e4b-it:free",
    "deepseek": "deepseek/deepseek-chat-v3-0324:free",
    "mistral": "mistralai/mistral-small-3.2-24b-instruct:free",
    "nvidia": "nvidia/llama-3.3-nemotron-super-49b-v1:free",
    "qwen": "qwen/qwen3-30b-a3b:free"
}
DEFAULT_MODEL = MODELS["deepseek"]
SYSTEM_PROMPT = "You are a helpful AI assistant."

MODEL_DESCRIPTIONS = {
    "gemma": "Gemma (Google): General-purpose, high-quality model.",
    "deepseek": "Deepseek: Fast, balanced, and reliable for most tasks.",
    "mistral": "Mistral: Good for creative and open-ended responses.",
    "nvidia": "Nvidia Llama: Large, advanced, and powerful model.",
    "qwen": "Qwen: Large, advanced, and multilingual model from Alibaba."
}

MODEL_PERSONALITIES = {
    "deepseek": "You are a balanced, logical, and concise assistant. Always provide clear, well-reasoned answers.",
    "gemma": "You are friendly, creative, and supportive. Respond in a warm, encouraging, and imaginative way.",
    "mistral": "You are imaginative, open-minded, and love exploring new ideas. Respond with creativity and curiosity.",
    "nvidia": "You are precise, technical, and thorough. Respond with detailed, expert-level information.",
    "qwen": "You are a multilingual, knowledgeable, and helpful assistant. Respond with clarity and global perspective."
}

FALLBACK_ORDER = ["deepseek", "mistral", "nvidia", "gemma", "qwen"]
