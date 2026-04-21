import streamlit as st
from groq import Groq

# --- COSTANTI ---
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
]

# --- CONFIGURAZIONE E SETUP ---
def init_page():
    """Configura l'aspetto della pagina e la sidebar."""
    st.set_page_config(page_title="Groq Professional Chat", page_icon="⚡")
    st.title("⚡ Groq Multi-Model Chat")
    
    with st.sidebar:
        st.header("Impostazioni Chat")
        # Il modello selezionato viene salvato in una variabile
        selected_model = st.selectbox(
            "Seleziona il modello AI:",
            options=MODELS,
            index=0  # Default sul primo della lista
        )
        
        st.divider()
        if st.button("Pulisci Cronologia"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Cronologia resettata. Come posso aiutarti?"}
            ]
            st.rerun()
            
    return selected_model

def get_client():
    """Inizializza il client Groq."""
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("Configura 'GROQ_API_KEY' nei Secrets!")
        st.stop()
    return Groq(api_key=api_key)

# --- GESTIONE MESSAGGI ---
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Ciao! Scegli un modello dalla barra a sinistra e iniziamo."}
        ]

def display_chat():
    """Visualizza tutti i messaggi nello stato della sessione."""
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

# --- LOGICA DI RISPOSTA ---
def handle_assistant_response(client, model_name):
    """Gestisce la chiamata API e lo streaming."""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=model_name,
                messages=[{"role": m["role"], "content": m["content"]} 
                          for m in st.session_state.messages],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Errore durante la generazione ({model_name}): {e}")

# --- MAIN LOOP ---
def main():
    # 1. Inizializzazione UI e recupero modello scelto
    selected_model = init_page()
    init_session_state()
    
    # 2. Visualizzazione storico
    display_chat()
    
    # 3. Input utente e risposta
    if prompt := st.chat_input("Scrivi qui..."):
        # Aggiunta messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Generazione risposta col modello scelto nella sidebar
        client = get_client()
        handle_assistant_response(client, selected_model)

if __name__ == "__main__":
    main()
