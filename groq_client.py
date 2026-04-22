import streamlit as st
from groq import Groq

class GroqChatClient:
    def __init__(self):
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def is_configured(self) -> bool:
        return self.client is not None

    def get_available_models(self) -> list:
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]

    def get_model_capabilities(self, model_id: str) -> str:
        capabilities = {
            "llama-3.3-70b-versatile": "Ideale per task complessi e multilingua. Ottimo bilanciamento tra logica e velocità.",
            "llama-3.1-8b-instant": "Il più veloce della serie Llama, perfetto per risposte rapide e compiti semplici.",
            "openai/gpt-oss-120b": "Flagship open-weight. Ragionamento di livello frontier, eccelle nel coding e nella sintesi complessa.",
            "openai/gpt-oss-20b": "Modello ultra-efficiente, ottimizzato per bassa latenza senza sacrificare troppo la precisione."
        }
        return capabilities.get(model_id, "Informazioni non disponibili.")

    def stream_chat_response(self, messages: list, model: str, temperature: float):
        try:
            return self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                stream=True
            )
        except Exception as e:
            st.error(f"Errore API: {e}")
            return None
