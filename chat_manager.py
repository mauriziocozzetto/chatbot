import streamlit as st

class ChatHistoryManager:
    def __init__(self):
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def sync_system_prompt(self, model_name: str):
        # Recuperiamo il numero attuale di messaggi utente
        user_count = self.count_user_messages()
        
        # Diciamo esplicitamente all'AI quanti messaggi l'utente ha inviato finora
        content = (
            f"Tu sei l'assistente AI basato sul modello {model_name}. "
            f"L'utente ha inviato finora {user_count} messaggi. "
            f"Se ti viene chiesto quanti messaggi sono stati inviati, "
            f"fai riferimento solo a questo numero: {user_count}."
        )
        
        if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
            st.session_state.messages.insert(0, {"role": "system", "content": content})
        else:
            st.session_state.messages[0]["content"] = content

    def add_message(self, role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})

    def count_user_messages(self) -> int:
        """Conta solo gli input dell'utente."""
        return sum(1 for m in st.session_state.messages if m["role"] == "user")

    def check_and_reset_if_limit_reached(self, max_user_messages: int):
        """Resetta tutto se il limite utente è raggiunto."""
        if self.count_user_messages() >= max_user_messages:
            self.clear_history()
            return True
        return False

    def clear_history(self):
        st.session_state.messages = []

    def get_messages(self):
        return st.session_state.messages
