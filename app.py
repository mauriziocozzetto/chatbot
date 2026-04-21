import streamlit as st
from groq import Groq

# --- COSTANTI E CONOSCENZA ---
MODELS_INFO = {
    "llama-3.3-70b-versatile": "Il modello più equilibrato e potente, ideale per ragionamenti complessi e conversazioni lunghe.",
    "llama-3.1-8b-instant": "Estremamente veloce e leggero. Perfetto per compiti semplici o risposte immediate.",
    "openai/gpt-oss-120b": "Modello ad alta capacità (se disponibile), ottimizzato per scrittura creativa e analisi approfondite.",
    "openai/gpt-oss-20b": "Versione più rapida della linea GPT-OSS, bilancia bene prestazioni e velocità."
}
MODELS = list(MODELS_INFO.keys())

# --- CONFIGURAZIONE E SETUP ---
def init_page():
    st.set_page_config(page_title="Groq Multi-Model", page_icon="⚡")
    st.title("⚡ Groq Expert Chat")
    
    with st.sidebar:
        st.header("Configurazione")
        selected_model = st.selectbox("Seleziona il modello AI:", options=MODELS)
        
        # Spiegazione automatica del modello selezionato
        st.info(f"**Opportunità:** {MODELS_INFO[selected_model]}")
        
        st.divider()
        if st.button("Pulisci Cronologia"):
            st.session_state.messages = []
            st.rerun()
            
    return selected_model

def get_system_prompt():
    """Genera il messaggio di sistema con la conoscenza dei modelli."""
    info_text = "\n".join([f"- {m}: {desc}" for m, desc in MODELS_INFO.items()])
    return {
        "role": "system", 
        "content": f"Sei un assistente esperto. Conosci i seguenti modelli disponibili in questa app:\n{info_text}\n"
                   "Se l'utente te lo chiede, spiega i vantaggi del modello che sta usando."
    }

# --- GESTIONE MESSAGGI ---
def init_session_state():
    """Inizializza lo stato includendo il messaggio di sistema."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Aggiungiamo il ruolo system (non visibile nella UI standard)
        st.session_state.messages.append(get_system_prompt())
        # Messaggio di benvenuto visibile
        st.session_state.messages.append(
            {"role": "assistant", "content": "Ciao! Ho caricato la conoscenza dei miei modelli. Chiedimi pure quali sono le differenze!"}
        )

def display_chat():
    """Visualizza solo i messaggi user e assistant (nasconde il system)."""
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])

# --- LOGICA DI RISPOSTA ---
def handle_assistant_response(client, model_name):
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Inviamo tutta la cronologia (incluso il system prompt in posizione 0)
            stream = client.chat.completions.create(
                model=model_name,
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Errore API: {e}")

# --- MAIN LOOP ---
def main():
    selected_model = init_page()
    init_session_state()
    display_chat()
    
    if prompt := st.chat_input("Chiedimi delle differenze tra i modelli..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        handle_assistant_response(client, selected_model)

if __name__ == "__main__":
    main()
